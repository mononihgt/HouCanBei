
import os
import pandas as pd
from pylab import *
from tqdm import tqdm


rcParams['figure.dpi'] = 300
rcParams['font.family'] = ['DejaVu Sans']


def setPath():
    global DIRNAME, RESULT_PATH, FIGURE_PATH, DATA_PATH
    DIRNAME = os.path.dirname(__file__)
    RESULT_PATH = os.path.join(DIRNAME, 'results')
    FIGURE_PATH = os.path.join(RESULT_PATH, 'figures')
    DATA_PATH = os.path.join(DIRNAME, 'rawdata')
    os.makedirs(os.path.join(RESULT_PATH,'scale',), exist_ok=True)
    

def deletePreviewsFiles(path:str=None):
    assert path is not None, "path should not be None"

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


def getSubjIndex():
    global dfNameIndex

    # deletePreviewsFiles(os.path.join(RESULT_PATH,'scale'))

    dfScale = pd.read_excel(os.path.join(DATA_PATH, 'scale', 'scale.xlsx'))
    dfScale = dfScale[['您的姓名', '焦虑因子', '抑郁因子', '总分']]

    name_index = []
    for root, dirs, files in os.walk(DATA_PATH, topdown=False):
        for file in tqdm(files):
            if 'exp' not in file:
                continue
            index = str(file[:-5].split('_')[-1])
            df = pd.read_excel(os.path.join(root, file),sheet_name='被试信息')
            name = df.iloc[-1,-1]
            info = {
                'name': name,
                'subj_idx': index
            }
            name_index.append(info)
    
    dfNameIndex = pd.DataFrame(name_index)
    dfNameIndex['anxiety'] = None
    dfNameIndex['depression'] = None
    dfNameIndex['HAMD'] = None
    for i, row in dfNameIndex.iterrows():
        name = row['name']
        if name =='张楚晨':
            continue
        row['anxiety'] = dfScale[dfScale['您的姓名'] == name]['焦虑因子'].values[0]
        row['depression'] = dfScale[dfScale['您的姓名'] == name]['抑郁因子'].values[0]
        row['HAMD'] = dfScale[dfScale['您的姓名'] == name]['总分'].values[0]
        
        dfNameIndex.iloc[i] = row
    
    dfNameIndex.to_excel(os.path.join(RESULT_PATH,'scale','name_index.xlsx'), index=False)
    
    return

def calculatePrimeIndex():
    
    for root, _, files in os.walk(FIGURE_PATH, topdown=False):
        for file in files:
            if not file.endswith('_grouped_wide.csv'):
                continue
            df = pd.read_csv(os.path.join(root, file))

            df['subj_idx'] = df['subj_idx'].astype(str)

            df['emotion_positivePrimeIndex'] = df['emotion_positive_negative'] - df['emotion_negative_negative']
            df['emotion_negativePrimeIndex'] = df['emotion_negative_positive'] - df['emotion_positive_positive']
            df['shape_positivePrimeIndex'] = df['shape_positive_negative'] - df['shape_negative_negative']
            df['shape_negativePrimeIndex'] = df['shape_negative_positive'] - df['shape_positive_positive']

            df['shape_positivePrime-negativePrime'] = df['shape_positive_negative'] + df['shape_positive_positive'] - (df['shape_negative_negative'] + df['shape_negative_positive'])
            df['emotion_positivePrime-negativePrime'] = df['emotion_positive_negative'] + df['emotion_positive_positive'] - (df['emotion_negative_negative'] + df['emotion_negative_positive'])

            df['test'] = df['emotion_positivePrimeIndex'] - df['emotion_negativePrimeIndex'] + df['shape_positivePrimeIndex'] - df['shape_negativePrimeIndex']
                                                                                                                                                                                                                                                                                                                                                           
            df = df.merge(dfNameIndex, on='subj_idx', how='left')

            df.drop(columns=['group'],inplace=True)
            df_withoutName = df.drop(columns=['name'], inplace=False)
            df_withoutName.to_csv(os.path.join(RESULT_PATH,'scale', f'{file[:-4]}_with_scale.csv'), index=False)
            df.to_excel(os.path.join(RESULT_PATH,'scale', f'{file[:-4]}_with_scale.xlsx'), index=False)

        # emotion_negative_negative	emotion_negative_positive	emotion_positive_negative	emotion_positive_positive	shape_negative_negative	shape_negative_positive	shape_positive_negative	shape_positive_positive



def main():
    setPath()
    getSubjIndex()

    calculatePrimeIndex()


if __name__ == '__main__':
    main()

