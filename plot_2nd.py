from pylab import *
import pandas as pd
import os
import matplotlib as mpl

mpl.rcParams.update({
    'text.color': 'black',
    'axes.labelcolor': 'black',
    'axes.edgecolor': 'black',
    'xtick.color': 'black',
    'ytick.color': 'black',
    'figure.edgecolor': 'black',
    'figure.facecolor': 'white',
})

rcParams['font.family'] = ['DejaVu Sans','Microsoft YaHei']
rcParams['figure.dpi'] = 300

def setPath():
    global DIRNAME, RESULT_PATH, FIGURE_PATH
    DIRNAME = os.path.dirname(__file__)
    RESULT_PATH = os.path.join(DIRNAME, 'lastDay')
    FIGURE_PATH = os.path.join(RESULT_PATH, 'figures')
    os.makedirs(FIGURE_PATH, exist_ok=True)
    return

def deletePreviewsFigures(path: str = None):
    assert path is not None, "path should not be None"
    for root, dirs, files in os.walk(path, topdown=False):
        
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    return

def readData(fileDir):
    global df
    assert fileDir is not None, "fileDir should not be None"
    df = pd.read_excel(os.path.join(fileDir, 'merged_trh.xlsx'))
    return


def plotFigure1():
    fig  = figure()
    ax = fig.add_subplot(111)
    groups = df['group'].unique()
    allDataShape = {}
    allDataEmotion = {}
    
    for group in groups:
        dfGroup = df[df['group'] == group]
        allDataShape[group] = dfGroup['shape_pos-neg'].values
        allDataEmotion[group] = dfGroup['emotion_pos-neg'].values

    fig = figure(figsize=(12,6))
    ax = fig.add_subplot(111)
    y_min,y_max = (0,0)
    for i, group in enumerate(groups):
        dataEmotion = allDataEmotion[group]
        dataShape = allDataShape[group]
        partShape = ax.violinplot(dataShape, positions=[i*3+0.5], showmeans=True, showmedians=False, widths=0.6)
        partEmotion = ax.violinplot(dataEmotion, positions=[i*3-0.5], showmeans=True, showmedians=False, widths=0.6)
        if i != len(groups)-1:
            ax.vlines([i*3+1.5], ymin=-500,  ymax=500, colors='#aaaaaa', linestyles='--', lw=1)
        from matplotlib.lines import Line2D
        proxy_shape   = Line2D([], [], color='#1f77b4', lw=2)   # 颜色可改
        proxy_emotion = Line2D([], [], color='#ff7f0e', lw=2)

        ax.legend([proxy_shape, proxy_emotion],
          ['形状任务', '情绪任务'],title = '注意诱导任务',loc = 'upper left')

        lines = ['cmins','cmaxes','cmeans','cbars']
        for line in lines:
            partShape[line].set_color('#1f77b4')
            partEmotion[line].set_color('#ff7f0e')

        for pc in partShape['bodies']:
            pc.set_facecolor('#1f77b4')

        for pc in partEmotion['bodies']:
            pc.set_facecolor('#ff7f0e')
            

        y_min = min(y_min, min(dataShape), min(dataEmotion))
        y_max = max(y_max, max(dataShape), max(dataEmotion))
    
    ax.set_xticks([i*3 for i in range(len(groups))])

    ax.set_xticklabels(groups, fontdict={'size': 14})
    x_min, x_max = ax.get_xlim()  
    dx = x_max - x_min
    ax.set_xlim(x_min - 0.01*dx, x_max - 0.01*dx)
    ax.tick_params(axis='x', which = 'both',length = 8, color = '#ffffff')

    dy = y_max-y_min
    ax.set_ylim(y_min - 0.18*dy, y_max + 0.18*dy)
    ax.set_ylabel('反应时差值（ms）',fontdict={'size': 16})

    ax.set_title('积极情绪阈下启动与消极情绪阈下启动的差值',fontdict={'size': 20},pad = 15)

    fig.savefig(os.path.join(FIGURE_PATH, 'figure1.png'),bbox_inches='tight')
    plt.close(fig)


def main():
    setPath()
    readData(fileDir=RESULT_PATH)
    deletePreviewsFigures(path=FIGURE_PATH)
    plotFigure1()

if __name__ == '__main__':
    main()




