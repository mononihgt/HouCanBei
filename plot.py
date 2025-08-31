from pylab import *
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

rcParams['figure.dpi'] = 300
rcParams['font.family'] = ['DejaVu Sans']

def setPath():
    global DIRNAME, RESULT_PATH, FIGURE_PATH
    DIRNAME = os.path.dirname(__file__)
    RESULT_PATH = os.path.join(DIRNAME, 'results')
    FIGURE_PATH = os.path.join(RESULT_PATH, 'figures')

    os.makedirs(FIGURE_PATH, exist_ok=True)

def deleteFigures(path:str=None):
    assert path is not None, "path should not be None"

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def drawFigures(result, group: str = None, subj: str = None, sem: np.ndarray = None, IV: str = None):
     # result shape: (2,2,2) induction(0:shape,1:emotion), prime_valence(0:negative,1:positive), target_valence(0:negative,1:positive)
    if sem is None:
        sem = np.zeros_like(result)
    margin = 0.05
    y_min = 0
    yRange = {
        'rt': (0, 1200),
        'pressDuration': (0, 300),
        'v': (-9, 9),
        'a': (0, 6),
        'sigma':(0,2.2),
        'x0':(-1,1),
        'nondectime':(0, 0.6)
    }
    y_min, y_max = yRange.get(IV, (None, None))
    
    assert None not in (y_min, y_max), f"yRange for IV '{IV}' is not defined."

    fig = figure()
    ax1 = fig.add_axes([0.1,0.1,0.4,0.8])
    ax2 = fig.add_axes([0.5,0.1,0.4,0.8])
    ax1.errorbar([1+margin,2+margin],result[0,:,0].flatten(),yerr=sem[0,:,0].flatten(),label = 'negative',marker = 'o',markersize=7,linestyle='-')
    ax1.errorbar([1-margin,2-margin],result[0,:,1].flatten(),yerr=sem[0,:,1].flatten(),label = 'positive',marker = '*',markersize=7,linestyle='-')

    ax1.set_xticks([1,2])
    ax1.set_xticklabels(['negative','positive'])
    
    x_min,x_max = ax1.get_xlim()
    # y_min,y_max = ax1.get_ylim()
    dx = (x_max - x_min) * 0.2
    # dy = (y_max - y_min) * 0.8
    ax1.set_xlim(x_min - dx, x_max + dx)
    ax1.set_ylim(y_min, y_max)
    ax1.set_title(f'induction:emotion')


    ax2.errorbar([1+margin,2+margin],result[1,:,0].flatten(),yerr=sem[1,:,0].flatten(),label = 'negative',marker = 'o',markersize=7,linestyle='-')
    ax2.errorbar([1-margin,2-margin],result[1,:,1].flatten(),yerr=sem[1,:,1].flatten(),label = 'positive',marker = '*',markersize=7,linestyle='-')

    ax2.set_xticks([1,2])
    ax2.set_xticklabels(['negative','positive'])

    x_min,x_max = ax2.get_xlim()
    # y_min,y_max = ax2.get_ylim()
    dx = (x_max - x_min) * 0.2
    # dy = (y_max - y_min) * 0.2
    ax2.set_xlim(x_min - dx, x_max + dx)
    ax2.set_ylim(y_min, y_max)
    ax2.set_yticks([])
    ax2.set_title(f'induction:shape')
    ax2.legend()
    fig.savefig(os.path.join(FIGURE_PATH, IV, f"{IV}_{group}_{subj}.png"), dpi=300)
    plt.close(fig)

def plotFigures(IV:str = None):
    
    assert IV is not None, "IV should not be None"
    
    os.makedirs(os.path.join(FIGURE_PATH, IV), exist_ok=True)
    deleteFigures(os.path.join(FIGURE_PATH, IV))

    if IV in ['rt','pressDuration']:
        dfRaw = pd.read_excel(os.path.join(RESULT_PATH,'mergedFile','merged_all_raw.xlsx'))
    
    else:
        dfRaw = pd.read_csv(os.path.join(RESULT_PATH,'DDM_2_2_2','traditional_ddm_results_2_2_2.csv'),encoding='gb18030')

    if IV == 'rt':
        column = '错误补救后按键反应时(ms)'
        dfRaw = dfRaw[dfRaw[column]<2000]

    elif IV == 'pressDuration':
        column = 'pressDuration'
        dfRaw = dfRaw[(dfRaw['rt']<2000) & (dfRaw['rt']>100)]
    else:
        column = IV

    groupBy = ['group','subj_idx','induction','prime_valence','target_valence']
    dfGrouped = dfRaw.groupby(groupBy).agg({column:'mean'}).reset_index()
    # dfGrouped.rename(columns={'错误补救后按键反应时(ms)':'rt'}, inplace=True)

    if IV == 'rt':
        dfGrouped.rename(columns={'错误补救后按键反应时(ms)':'rt'}, inplace=True)
        column = 'rt'
    
    dfGrouped['condition'] = (
        dfGrouped['induction'] + '_' +
        dfGrouped['prime_valence'] + '_' +
        dfGrouped['target_valence']
    )

    # 2. pivot：行 = 被试，列 = 8 条件，值 = v
    dfGrouped_wide = (dfGrouped
            .pivot_table(index=['group', 'subj_idx'],
                        columns='condition',
                        values=column)
            .reset_index())

    dfGrouped.to_csv(os.path.join(FIGURE_PATH, IV, f'{IV}_grouped.csv'), index=False, encoding='gb18030')
    dfGrouped_wide.to_csv(os.path.join(FIGURE_PATH, IV, f'{IV}_grouped_wide.csv'), index=False, encoding='gb18030')
    
    groups = dfGrouped['group'].unique()
    for group in groups:
        dfGroup = dfGrouped[dfGrouped['group'] == group]
        subjs = dfGroup['subj_idx'].unique()
        results = np.zeros((len(subjs), 2, 2, 2))
        for i, subj in enumerate(tqdm(subjs, desc=f"Processing {group} group")):
            dfSubj = dfGroup[dfGroup['subj_idx'] == subj]
            result = dfSubj[column].values.reshape(2,2,2)
            results[i,:,:,:] = result
            drawFigures(result, group, subj, IV=IV)
        results_mean = results.mean(axis=0)
        results_sem = results.std(axis=0) / np.sqrt(results.shape[0])
        drawFigures(results_mean, group=group, subj='mean',sem=results_sem, IV = IV)

def main():
    setPath()
    plotFigures(IV = 'rt')
    plotFigures(IV = 'pressDuration')
    ddmParams = ['v','sigma','a','x0','nondectime']
    for param in ddmParams:
        plotFigures(IV = param)


if __name__ == '__main__':
    main()