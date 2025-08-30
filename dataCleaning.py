import pandas as pd
import os
from tqdm import tqdm

def defineUnqualifiedSubjects():
    global unqualifiedSubjects
    unqualifiedSubjects = ['55758322','55760307','55916641']

def setPaths():
    global DIRNAME, DATA_PATH, RESULT_PATH
    DIRNAME = os.path.dirname(__file__)
    DATA_PATH = os.path.join(DIRNAME,'rawData')
    RESULT_PATH = os.path.join(DIRNAME, 'results')
    return

def createResultDirectories():
    os.makedirs(os.path.join(DIRNAME, 'results'), exist_ok=True)
    os.makedirs(os.path.join(DIRNAME, 'results','visibilityTest'), exist_ok=True)
    os.makedirs(os.path.join(DIRNAME, 'results','mergedFile'), exist_ok=True)

def deletePreviewsFiles(dirname:str=None):
    assert dirname is not None, "dirname should not be None"

    for root, dirs, files in os.walk(dirname, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

    return

def cleanData():
    dfMergedAll = pd.DataFrame()
    dfMergedAllRaw = pd.DataFrame()
    groups = ['normal', 'depression']
    for group in groups:
        dataPath = os.path.join(DATA_PATH, group)
        files = [f for f in os.listdir(dataPath) 
                if (os.path.isfile(os.path.join(dataPath, f)) and f.endswith('.xlsx') and f.startswith('experiment'))]
        dfMerged = pd.DataFrame()
        dfMergedRaw = pd.DataFrame()
        visibilityTest= pd.DataFrame()
        for file in tqdm(files):

            if file[:-5].split('_')[-1] in unqualifiedSubjects:
                continue

            subjectID = file[:-5].split('_')[-1]
            
            df_1 = pd.read_excel(os.path.join(dataPath, file),sheet_name='试次数据')
            df_2 = pd.read_excel(os.path.join(dataPath, file),sheet_name='原始反应时数据')
            df_3 = pd.read_excel(os.path.join(dataPath, file),sheet_name='阈限验证任务数据')
            
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
            df['target_valence'] = df['target_valence'].replace({'积极':'positive','消极':'negative'})
            df['response'] = df['response'].replace({'是':'1','否':'0'})
            df['induction'] = df['induction'].replace({'形状任务':'shape','情绪任务':'emotion'})
            df_raw = df.copy()
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
            dfMergedRaw = pd.concat([dfMergedRaw, df_raw], ignore_index=True)

        dfMerged['group'] = group
        dfMergedRaw['group'] = group

        dfMergedAll = pd.concat([dfMergedAll, dfMerged], ignore_index=True)
        dfMergedAllRaw = pd.concat([dfMergedAllRaw, dfMergedRaw], ignore_index=True)
        dfMerged.to_excel(os.path.join(RESULT_PATH, 'mergedFile', f'merged_{group}.xlsx'), index=False)
        visibilityTest.to_excel(os.path.join(RESULT_PATH, 'visibilityTest',f'visibilityTest_{group}.xlsx'), index=False)
        with open(os.path.join(RESULT_PATH, 'visibilityTest',f'visibilityTest_{group}_summary.txt'), 'w') as f:
            f.write(f'平均准确率: {visibilityTest["准确率"].mean()}\n')
            f.write(f'平均阈限刺激强度(帧): {visibilityTest["刺激强度(帧)"].mean()}\n')
            f.write(f'平均阈限刺激时间(毫秒): {visibilityTest["刺激时间(毫秒)"].mean()}\n')
            f.write(f'被试数量: {visibilityTest["subj_idx"].nunique()}\n')
        f.close()
    dfMergedAll['pressDuration'] = dfMergedAll['松键反应时(ms)']- dfMergedAll['rt']
    dfMergedAllRaw['pressDuration'] = dfMergedAllRaw['松键反应时(ms)']- dfMergedAllRaw['rt']
    dfMergedAll.to_excel(os.path.join(RESULT_PATH, 'mergedFile', 'merged_all.xlsx'), index=False)
    dfMergedAllRaw.to_excel(os.path.join(RESULT_PATH, 'mergedFile', 'merged_all_raw.xlsx'), index=False)
    
    return

if __name__ == '__main__':
    setPaths()
    defineUnqualifiedSubjects()
    deletePreviewsFiles(os.path.join(RESULT_PATH,'mergedFile'))
    deletePreviewsFiles(os.path.join(RESULT_PATH,'visibilityTest'))
    createResultDirectories()
    cleanData()
