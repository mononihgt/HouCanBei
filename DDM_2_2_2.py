import pandas as pd
import numpy as np
import pyddm, os
from pyddm import Model, Fittable
from pyddm import Sample, Model, Fittable
from pyddm.models import DriftConstant, NoiseConstant, BoundConstant, ICPointRatio, OverlayNonDecision
import warnings
from tqdm import tqdm
warnings.filterwarnings('ignore')  # 忽略拟合过程中的警告

RESULT_PATH = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(os.path.join(RESULT_PATH,'DDM_2_2_2'), exist_ok=True)
ddmPath = os.path.join(RESULT_PATH,'DDM_2_2_2')

def deletePreviewsFiles():
    # 如果Result path内存在任何文件或文件夹，则删除resultpath内所有文件和文件夹
    for root, dirs, files in os.walk(ddmPath, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def responseTransform(row):
    if row['target_valence'] == 'negative':
        if row['response'] == 0:
            return 1  # 将积极反应编码为1
        else:
            return 0  # 将消极反应编码为0
    else:
        return row['response']  # 其他情况保持不变

def main():
    # 假设您的数据已经加载到DataFrame中，包含以下列：
    # 'subj_idx', 'induction', 'prime_valence', 'target_valence', 'rt', 'response'
    # 其中response编码为0(消极)或1(积极)

    df = pd.read_excel(os.path.join(RESULT_PATH, 'mergedFile', 'merged_all.xlsx'))

    # 初始化一个字典来存储所有结果
    results = pd.DataFrame()

    # 获取所有唯一的被试ID
    subjects = df['subj_idx'].unique()

    df['responseForDDM'] = df.apply(responseTransform, axis=1)

    df['condition'] = (
        df['induction'].astype(str) + '_' +
        df['prime_valence'].astype(str) + '_' +
        df['target_valence'].astype(str)
    )
    conditions = df['condition'].unique()

    # 循环遍历每个被试
    for idx in tqdm(range(len(subjects))):
    # for idx in tqdm(range(1)):
        subject = subjects[idx]
        print(f"处理被试: {subject}")
        param = {}
        # 循环遍历每种诱导条件
        for cond in conditions:
            condition_data = df[
                (df['subj_idx'] == subject) &
                (df['condition'] == cond)
            ]
            group = condition_data['group'].unique()[0]

            induction = condition_data['induction'].unique()[0]
            prime_valence = condition_data['prime_valence'].unique()[0]
            target_valence = condition_data['target_valence'].unique()[0]
            
            if len(condition_data) < 10:  # 设置一个最小试次数阈值
                print(f"  跳过条件 - 诱导{induction}, 启动{prime_valence}, 目标{target_valence}: 只有{len(condition_data)}个试次")
                continue
            
            print(f"  拟合条件 - 诱导{induction}, 启动{prime_valence}, 目标{target_valence}: {len(condition_data)}个试次")
            
            # 准备DDM拟合所需的数据格式
            # 在传统DDM中，我们需要将选择编码为0(下边界)和1(上边界)
            # 假设您的实验设计中，上边界对应"积极"反应，下边界对应"消极"反应
            choices = condition_data['responseForDDM'].values  # 已经是0或1
            rts = condition_data['rt'].values / 1000  # 转换为秒

            # 创建样本对象
            dfsample = pd.DataFrame({
                'rt': rts,
                'choice': choices,
                # 'condition': condition_values  # 如果有条件的话
            })

            sample = pyddm.Sample.from_pandas_dataframe(dfsample, rt_column_name='rt', choice_column_name='choice')
            
            # 定义DDM模型
            # 使用可拟合参数，设置合理的初始值和边界
            
            # 3.3 定义标准 4 参数 DDM
            m = Model(
                name=f'subj_idx_{subject}_ind{induction}_p{prime_valence}_t{target_valence}',
                drift   = DriftConstant(drift=Fittable(name='drift', minval=-8, maxval=8)),
                noise   = NoiseConstant(noise=Fittable(name='noise', minval=0.5, maxval=2)),
                bound   = BoundConstant(B=Fittable(name='B', minval=0.3, maxval=3)),
                IC      = ICPointRatio(x0=Fittable(name='x0', minval=-0.9, maxval=0.9)),
                overlay = OverlayNonDecision(nondectime=Fittable(name='nondectime', minval=0.2, maxval=0.6)),
                dt = 0.001
            )
            
            # 拟合模型
            try:
                m.fit(sample, lossfunction=pyddm.LossRobustLikelihood, verbose=False)

                pars = dict(zip(m.get_model_parameter_names(), m.get_model_parameters()))

                # 3.5 保存估计值
                param[cond] = {
                    'subj_idx': subject,
                    'induction': induction,
                    'prime_valence': prime_valence,
                    'target_valence': target_valence,
                    'v': float(pars['drift']),
                    'sigma': float(pars['noise']),
                    'a': float(pars['B']) * 2,
                    'x0': float(pars['x0']),
                    'nondectime': float(pars['nondectime']),
                    'n_trials': len(condition_data),
                    'accuracy': condition_data['response'].mean(),
                    'group': group,
                    'error': None
                }
                print(f'it\'s ok in condition {cond}')

            except Exception as e:
                print(f"    拟合失败: {e}")
                # 存储失败信息
                param[cond]={
                    'subj_idx': subject,
                    'induction': induction,
                    'prime_valence': prime_valence,
                    'target_valence': target_valence,
                    'v': float(pars['drift']),
                    'sigma': float(pars['noise']),
                    'a': float(pars['B']) * 2,
                    'x0': float(pars['x0']),
                    'nondectime': float(pars['nondectime']),
                    'n_trials': len(condition_data),
                    'accuracy': condition_data['response'].mean(),
                    'group': group,
                    'error': str(e)
                }

        df_subject = pd.DataFrame(param).T
        df_subject.to_csv(os.path.join(ddmPath, f'subj_idx_{subject}.csv'), index=False)
        results = pd.concat([results, df_subject], axis=0)


    # 保存结果到CSV文件
    results.to_csv(os.path.join(ddmPath, 'traditional_ddm_results_2_2_2.csv'), index=False)

    print("拟合完成! 结果已保存到 traditional_ddm_results_2_2_2.csv")


if __name__ == '__main__':
    deletePreviewsFiles()
    main()