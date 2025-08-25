import pandas as pd
import os
from tqdm import tqdm

def defineUnqualifiedSubjects():
    global unqualifiedSubjects
    unqualifiedSubjects = ['55758322','55760307','55916641']

def setPaths():
    global DIRNAME, DATA_PATH, RESULT_PATH
    DIRNAME = os.path.dirname(__file__)
    DATA_PATH = os.path.join(DIRNAME,'rawData','normal')
    os.makedirs(os.path.join(DIRNAME, 'results'), exist_ok=True)
    os.makedirs(os.path.join(DIRNAME, 'results','visibilityTest'), exist_ok=True)
    RESULT_PATH = os.path.join(DIRNAME, 'results')
    return

def deletePreviewsFiles():
    os.remove(os.path.join(DATA_PATH, 'merged.xlsx'))
    if os.path.exists(os.path.join(RESULT_PATH, 'visibilityTest','visibilityTest.xlsx')):
        os.remove(os.path.join(RESULT_PATH, 'visibilityTest','visibilityTest.xlsx'))
        os.remove(os.path.join(RESULT_PATH, 'visibilityTest','visibilityTest_summary.txt'))
    return

def cleanData():
    files = [f for f in os.listdir(DATA_PATH) 
             if (os.path.isfile(os.path.join(DATA_PATH, f)) and f.endswith('.xlsx') and f.startswith('experiment'))]
    dfMerged = pd.DataFrame()
    visibilityTest= pd.DataFrame()
    for file in tqdm(files):

        if file[:-5].split('_')[-1] in unqualifiedSubjects:
            continue

        subjectID = file[:-5].split('_')[-1]
        
        df_1 = pd.read_excel(os.path.join(DATA_PATH, file),sheet_name='试次数据')
        df_2 = pd.read_excel(os.path.join(DATA_PATH, file),sheet_name='原始反应时数据')
        df_3 = pd.read_excel(os.path.join(DATA_PATH, file),sheet_name='阈限验证任务数据')
        
        df_1['启动刺激情绪类型'] = df_1['错误补救后主任务按键']
        df = pd.concat([df_2, df_1[['注意诱导任务说明','启动刺激情绪类型']]], axis=1)
        df['subj_idx'] = subjectID
        df.rename(columns={
            '注意诱导任务说明':'induction',
            '启动刺激情绪类型':'prime_valence',
            '情绪类型':'target_valence',
            '是否正确':'response',
            '按键反应时(ms)':'rt'
        },inplace=True)
        df['target_valence'].replace({'积极':'positive','消极':'negative'}, inplace=True)
        df['response'].replace({'是':'1','否':'0'}, inplace=True)
        df = df[df['rt']<2000]
        
        thresholdOfFrame = df_3['刺激强度(帧)'].values[0]
        thresholdOfDuration = df_3['刺激时间(毫秒)'].values[0]
        accuracy = len(df_3[df_3['是否正确']=='是'])/len(df_3)
        dictTemp = {
            'subj_idx': subjectID,
            '刺激强度(帧)': thresholdOfFrame,
            '刺激时间(毫秒)': thresholdOfDuration,
            '准确率': accuracy
        }
        
        visibilityTest = pd.concat([visibilityTest, pd.DataFrame([dictTemp])], ignore_index=True)
        dfMerged = pd.concat([dfMerged, df], ignore_index=True)

    dfMerged.to_excel(os.path.join(DATA_PATH, 'merged.xlsx'), index=False)
    visibilityTest.to_excel(os.path.join(RESULT_PATH, 'visibilityTest','visibilityTest.xlsx'), index=False)
    with open(os.path.join(RESULT_PATH, 'visibilityTest','visibilityTest_summary.txt'), 'w') as f:
        f.write(f'平均准确率: {visibilityTest["准确率"].mean()}\n')
        f.write(f'平均阈限刺激强度(帧): {visibilityTest["刺激强度(帧)"].mean()}\n')
        f.write(f'平均阈限刺激时间(毫秒): {visibilityTest["刺激时间(毫秒)"].mean()}\n')
        f.write(f'被试数量: {visibilityTest["subj_idx"].nunique()}\n')
    f.close()

    return

if __name__ == '__main__':
    setPaths()
    defineUnqualifiedSubjects()
    if 'merged.xlsx' in os.listdir(DATA_PATH):
        deletePreviewsFiles()
    cleanData()
