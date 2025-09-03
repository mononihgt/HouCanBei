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
    fig = figure(figsize=(12,5))
    groups = df['group'].unique()
    allDataShape = {}
    allDataEmotion = {}
    
    for group in groups:
        dfGroup = df[df['group'] == group]
        allDataShape[group] = dfGroup['shape_pos-neg'].values
        allDataEmotion[group] = dfGroup['emotion_pos-neg'].values

    ax = fig.add_subplot(111)
    y_min, y_max = (0, 0)
    
    bar_width = 0.6
    for i, group in enumerate(groups):
        dataEmotion = allDataEmotion[group]
        dataShape = allDataShape[group]
        
        # Calculate means and standard errors
        shape_mean = np.mean(dataShape)
        shape_error = np.std(dataShape) / np.sqrt(len(dataShape))
        emotion_mean = np.mean(dataEmotion)
        emotion_error = np.std(dataEmotion) / np.sqrt(len(dataEmotion))
        
        # Create bar plots instead of violin plots
        ax.bar(i*3+0.5, shape_mean, width=bar_width, yerr=shape_error, color='#1f77b4', capsize=5, label='形状任务' if i == 0 else '')
        ax.bar(i*3-0.5, emotion_mean, width=bar_width, yerr=emotion_error, color='#ff7f0e', capsize=5, label='情绪任务' if i == 0 else '')
        
        if i != len(groups)-1:
            ax.vlines([i*3+1.5], ymin=-500, ymax=500, colors='#aaaaaa', linestyles='--', lw=1)

        y_min = min(y_min, shape_mean - shape_error, emotion_mean - emotion_error)
        y_max = max(y_max, shape_mean + shape_error, emotion_mean + emotion_error)

    
    # Add horizontal line at y=0
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1.0)
    
    # Hide top, right and bottom spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    # Legend
    ax.legend(title='注意诱导任务', loc='upper left')
    
    ax.set_xticks([i*3 for i in range(len(groups))])
    ax.set_xticklabels(groups, fontdict={'size': 12})
    x_min, x_max = ax.get_xlim()  
    dx = x_max - x_min
    ax.set_xlim(x_min - 0.01*dx, x_max - 0.01*dx)
    ax.tick_params(axis='x', which='both', length=8, color='#ffffff')

    dy = y_max-y_min
    ax.set_ylim(y_min - 0.18*dy, y_max + 0.18*dy)
    ax.set_ylabel('反应时差值（ms）', fontdict={'size': 16})
    ax.set_title('积极情绪阈下启动与消极情绪阈下启动的反应时差值', fontdict={'size': 20}, pad=15)

    fig.savefig(os.path.join(FIGURE_PATH, 'figure1.png'), bbox_inches='tight')
    plt.close(fig)

def plotFigure2():
    fig = figure(figsize=(12,5))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    groups = df['group'].unique()
    allDataShape = {}
    allDataEmotion = {}
    
    for group in groups:
        dfGroup = df[df['group'] == group]
        allDataShape[group] = dfGroup['shape_pos-neg'].values
        allDataEmotion[group] = dfGroup['emotion_pos-neg'].values

    y_min, y_max = (0, 0)
    bar_width = 0.7
    
    for i, group in enumerate(groups):
        dataEmotion = allDataEmotion[group]
        dataShape = allDataShape[group]
        
        # Calculate means and standard errors
        shape_mean = np.mean(dataShape)
        shape_error = np.std(dataShape) / np.sqrt(len(dataShape))
        emotion_mean = np.mean(dataEmotion)
        emotion_error = np.std(dataEmotion) / np.sqrt(len(dataEmotion))
        if i== 0:
            # Create bar plots instead of violin plots
            ax1.bar(i*1.5, shape_mean, width=bar_width, yerr=shape_error, color='#1f77b4', capsize=3,error_kw = {'linewidth': 1.0}, label='形状诱导任务')
            ax2.bar(i*1.5, emotion_mean, width=bar_width, yerr=emotion_error, color='#ff7f0e', capsize=3, error_kw = {'linewidth': 1.0}, label='情绪诱导任务')
        else:
            ax1.bar(i*1.5, shape_mean, width=bar_width, yerr=shape_error, color='#1f77b4', capsize=3,error_kw = {'linewidth': 1.0})
            ax2.bar(i*1.5, emotion_mean, width=bar_width, yerr=emotion_error, color='#ff7f0e', capsize=3,error_kw = {'linewidth': 1.0})

        y_min = min(y_min, shape_mean - shape_error, emotion_mean - emotion_error)
        y_max = max(y_max, shape_mean + shape_error, emotion_mean + emotion_error)

    ax1.legend()
    ax2.legend()

    for ax in [ax1, ax2]:
        # Add horizontal line at y=0
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1.0)
        
        # Hide top, right and bottom spines
        # ax.spines['top'].set_visible(False)
        # ax.spines['right'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        

        ax.set_xticks([i*1.5 for i in range(len(groups))])
        ax.set_xticklabels(groups, fontdict={'size': 12},rotation=30)
        ax.tick_params(axis='x', which='both', length=5, color="#000000")
        # ax.set_title('情绪诱导任务时阈下启动的反应时差值', fontdict={'size': 16}, pad=5)

        # ax.set_title('形状诱导任务时阈下启动的反应时差值', fontdict={'size': 16}, pad=5)

        x_min, x_max = ax.get_xlim()
        dx = x_max - x_min
        ax.set_xlim(x_min - 0.04*dx, x_max + 0.04*dx)
        dy = y_max-y_min
        ax.set_ylim(y_min - 0.15*dy, y_max + 0.15*dy)
        ax.set_ylabel('积极启动-消极启动反应时差值（ms）', fontdict={'size': 12})
    

    fig.savefig(os.path.join(FIGURE_PATH, 'figure2.png'), bbox_inches='tight')
    plt.close(fig)


def plotFigure3():
    fig = figure(figsize=(12,5))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    groups = df['group'].unique()
    allDataShape = {}
    allDataEmotion = {}
    
    groups = np.setdiff1d(groups, ['抑郁恢复','未成年抑郁'])

    for group in groups:
        dfGroup = df[df['group'] == group]
        allDataShape[group] = dfGroup['shape_pos-neg'].values
        allDataEmotion[group] = dfGroup['emotion_pos-neg'].values

    y_min, y_max = (0, 0)
    bar_width = 0.6
    
    for i, group in enumerate(groups):
        dataEmotion = allDataEmotion[group]
        dataShape = allDataShape[group]
        
        # Calculate means and standard errors
        shape_mean = np.mean(dataShape)
        shape_error = np.std(dataShape) / np.sqrt(len(dataShape))
        emotion_mean = np.mean(dataEmotion)
        emotion_error = np.std(dataEmotion) / np.sqrt(len(dataEmotion))
        if i== 0:
            # Create bar plots instead of violin plots
            ax1.bar(i*1.2, shape_mean, width=bar_width, yerr=shape_error, color='#1f77b4', capsize=3,error_kw = {'linewidth': 1.0}, label='形状诱导任务')
            ax2.bar(i*1.2, emotion_mean, width=bar_width, yerr=emotion_error, color='#ff7f0e', capsize=3, error_kw = {'linewidth': 1.0}, label='情绪诱导任务')
        else:
            ax1.bar(i*1.2, shape_mean, width=bar_width, yerr=shape_error, color='#1f77b4', capsize=3,error_kw = {'linewidth': 1.0})
            ax2.bar(i*1.2, emotion_mean, width=bar_width, yerr=emotion_error, color='#ff7f0e', capsize=3,error_kw = {'linewidth': 1.0})

        y_min = min(y_min, shape_mean - shape_error, emotion_mean - emotion_error)
        y_max = max(y_max, shape_mean + shape_error, emotion_mean + emotion_error)

    ax1.legend()
    ax2.legend()

    for ax in [ax1, ax2]:
        # Add horizontal line at y=0
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1.0)
        
        # Hide top, right and bottom spines
        # ax.spines['top'].set_visible(False)
        # ax.spines['right'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        

        ax.set_xticks([i*1.2 for i in range(len(groups))])
        ax.set_xticklabels(groups, fontdict={'size': 12})
        ax.tick_params(axis='x', which='both', length=5, color="#000000")
        # ax.set_title('情绪诱导任务时阈下启动的反应时差值', fontdict={'size': 16}, pad=5)

        # ax.set_title('形状诱导任务时阈下启动的反应时差值', fontdict={'size': 16}, pad=5)

        x_min, x_max = ax.get_xlim()
        dx = x_max - x_min
        ax.set_xlim(x_min - 0.04*dx, x_max + 0.04*dx)
        dy = y_max-y_min
        ax.set_ylim(y_min - 0.18*dy, y_max + 0.18*dy)
        ax.set_ylabel('积极启动-消极启动反应时差值（ms）', fontdict={'size': 12})
    

    fig.savefig(os.path.join(FIGURE_PATH, 'figure3.png'), bbox_inches='tight')
    plt.close(fig)

def plotFigure4():
    fig = figure(figsize=(12,5))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    groups = df['group'].unique()
    allDataShapePos = {}
    allDataShapeNeg = {}
    
    groups = np.setdiff1d(groups, ['抑郁恢复','未成年抑郁'])

    for group in groups:
        dfGroup = df[df['group'] == group]
        allDataShapePos[group] = dfGroup['shapePosPrimeIndex'].values
        allDataShapeNeg[group] = dfGroup['shapeNegPrimeIndex'].values

    y_min, y_max = (0, 0)
    bar_width = 0.6
    
    for i, group in enumerate(groups):
        dataShapeNeg = allDataShapeNeg[group]
        dataShapePos = allDataShapePos[group]
        
        # Calculate means and standard errors
        shapePos_mean = np.mean(dataShapePos)
        shapePos_error = np.std(dataShapePos) / np.sqrt(len(dataShapePos))
        ShapeNeg_mean = np.mean(dataShapeNeg)
        ShapeNeg_error = np.std(dataShapeNeg) / np.sqrt(len(dataShapeNeg))
        if i== 0:
            # Create bar plots instead of violin plots
            ax1.bar(i*1.2, shapePos_mean, width=bar_width, yerr=shapePos_error, color='#1f77b4', capsize=3,error_kw = {'linewidth': 1.0}, label='积极启动')
            ax2.bar(i*1.2, ShapeNeg_mean, width=bar_width, yerr=ShapeNeg_error, color='#ff7f0e', capsize=3, error_kw = {'linewidth': 1.0}, label='消极启动')
        else:
            ax1.bar(i*1.2, shapePos_mean, width=bar_width, yerr=shapePos_error, color='#1f77b4', capsize=3,error_kw = {'linewidth': 1.0})
            ax2.bar(i*1.2, ShapeNeg_mean, width=bar_width, yerr=ShapeNeg_error, color='#ff7f0e', capsize=3,error_kw = {'linewidth': 1.0})

        y_min = min(y_min, shapePos_mean - shapePos_error, ShapeNeg_mean - ShapeNeg_error)
        y_max = max(y_max, shapePos_mean + shapePos_error, ShapeNeg_mean + ShapeNeg_error)

    ax1.legend()
    ax2.legend()

    for ax in [ax1, ax2]:
        # Add horizontal line at y=0
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1.0)
        
        # Hide top, right and bottom spines
        # ax.spines['top'].set_visible(False)
        # ax.spines['right'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        

        ax.set_xticks([i*1.2 for i in range(len(groups))])
        ax.set_xticklabels(groups, fontdict={'size': 12})
        ax.tick_params(axis='x', which='both', length=5, color="#000000")
        # ax.set_title('情绪诱导任务时阈下启动的反应时差值', fontdict={'size': 16}, pad=5)

        # ax.set_title('形状诱导任务时阈下启动的反应时差值', fontdict={'size': 16}, pad=5)

        x_min, x_max = ax.get_xlim()
        dx = x_max - x_min
        ax.set_xlim(x_min - 0.04*dx, x_max + 0.04*dx)
        dy = y_max-y_min
        ax.set_ylim(y_min - 0.18*dy, y_max + 0.18*dy)
    ax1.set_ylabel('形状诱导任务积极阈下启动效应', fontdict={'size': 12})
    ax2.set_ylabel('形状诱导任务消极阈下启动效应', fontdict={'size': 12})

    fig.savefig(os.path.join(FIGURE_PATH, 'figure4.png'), bbox_inches='tight')
    plt.close(fig)

def plotFigure5():
    fig = figure(figsize=(12,5))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    groups = df['group'].unique()
    allDataEmotionPos = {}
    allDataEmotionNeg = {}
    
    groups = np.setdiff1d(groups, ['抑郁恢复','未成年抑郁'])

    for group in groups:
        dfGroup = df[df['group'] == group]
        allDataEmotionPos[group] = dfGroup['emoPosPrimeIndex'].values
        allDataEmotionNeg[group] = dfGroup['emoNegPrimeIndex'].values

    y_min, y_max = (0, 0)
    bar_width = 0.6
    
    for i, group in enumerate(groups):
        dataEmotionNeg = allDataEmotionNeg[group]
        dataEmotionPos = allDataEmotionPos[group]
        
        # Calculate means and standard errors
        EmotionPos_mean = np.mean(dataEmotionPos)
        EmotionPos_error = np.std(dataEmotionPos) / np.sqrt(len(dataEmotionPos))
        EmotionNeg_mean = np.mean(dataEmotionNeg)
        EmotionNeg_error = np.std(dataEmotionNeg) / np.sqrt(len(dataEmotionNeg))
        if i== 0:
            # Create bar plots instead of violin plots
            ax1.bar(i*1.2, EmotionPos_mean, width=bar_width, yerr=EmotionPos_error, color='#1f77b4', capsize=3,error_kw = {'linewidth': 1.0}, label='积极启动')
            ax2.bar(i*1.2, EmotionNeg_mean, width=bar_width, yerr=EmotionNeg_error, color='#ff7f0e', capsize=3, error_kw = {'linewidth': 1.0}, label='消极启动')
        else:
            ax1.bar(i*1.2, EmotionPos_mean, width=bar_width, yerr=EmotionPos_error, color='#1f77b4', capsize=3,error_kw = {'linewidth': 1.0})
            ax2.bar(i*1.2, EmotionNeg_mean, width=bar_width, yerr=EmotionNeg_error, color='#ff7f0e', capsize=3,error_kw = {'linewidth': 1.0})

        y_min = min(y_min, EmotionPos_mean - EmotionPos_error, EmotionNeg_mean - EmotionNeg_error)
        y_max = max(y_max, EmotionPos_mean + EmotionPos_error, EmotionNeg_mean + EmotionNeg_error)

    ax1.legend()
    ax2.legend()

    for ax in [ax1, ax2]:
        # Add horizontal line at y=0
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1.0)
        
        # Hide top, right and bottom spines
        # ax.spines['top'].set_visible(False)
        # ax.spines['right'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        

        ax.set_xticks([i*1.2 for i in range(len(groups))])
        ax.set_xticklabels(groups, fontdict={'size': 12})
        ax.tick_params(axis='x', which='both', length=5, color="#000000")
        # ax.set_title('情绪诱导任务时阈下启动的反应时差值', fontdict={'size': 16}, pad=5)

        # ax.set_title('形状诱导任务时阈下启动的反应时差值', fontdict={'size': 16}, pad=5)

        x_min, x_max = ax.get_xlim()
        dx = x_max - x_min
        ax.set_xlim(x_min - 0.04*dx, x_max + 0.04*dx)
        dy = y_max-y_min
        ax.set_ylim(y_min - 0.18*dy, y_max + 0.18*dy)
    ax1.set_ylabel('情绪诱导任务积极阈下启动效应', fontdict={'size': 12})
    ax2.set_ylabel('情绪诱导任务消极阈下启动效应', fontdict={'size': 12})

    fig.savefig(os.path.join(FIGURE_PATH, 'figure5.png'), bbox_inches='tight')
    plt.close(fig)

def plotCorrelation():
    import seaborn as sns
    import matplotlib.pyplot as plt

    from scipy.stats import pearsonr

    scales = ['shape_pos-neg', 'emotion_pos-neg', 'shapePosPrimeIndex', 'shapeNegPrimeIndex', 'emoPosPrimeIndex', 'emoNegPrimeIndex', 'anxiety', 'depression', 'hamd']

    # 创建 PairGrid
    g = sns.PairGrid(df[scales])

    # 在下三角绘制散点图并添加趋势线和置信区间
    g.map_lower(sns.regplot, scatter_kws={'alpha': 0.6}, line_kws={'color': '#A55F89'})

    # 在对角线绘制核密度估计图
    g.map_diag(sns.kdeplot, fill=True)

    # 在上三角标注相关系数和显著性水平
    def corr_func(x, y, **kws):
        r, p = pearsonr(x, y)  # 计算 Pearson 相关系数和 p 值
        ax = plt.gca()
        ax.annotate(f'r = {r:.2f}\np = {p:.3f}', xy=(0.5, 0.5), xycoords='axes fraction', 
                    ha='center', va='center', fontsize=18, color='#5074B0')

    g.map_upper(corr_func)

    # 调整坐标轴标签和刻度标签的大小
    for ax in g.axes.flatten():
        # 设置 x 轴和 y 轴标签的大小
        ax.set_xlabel(ax.get_xlabel(), fontsize=20,rotation=45)
        ax.set_ylabel(ax.get_ylabel(), fontsize=20,rotation=45)

        # 设置 x 轴和 y 轴刻度标签的大小
        ax.tick_params(axis='both', labelsize=15)
    

# 添加标题
# plt.suptitle('Pairplot of Scales with Trend Lines and Correlation', y=1.02)

    plt.savefig(os.path.join(FIGURE_PATH, 'figure6.png'), bbox_inches='tight')
    plt.close()


def main():
    setPath()
    readData(fileDir=RESULT_PATH)
    deletePreviewsFigures(path=FIGURE_PATH)
    plotFigure1()
    plotFigure2()
    plotFigure3()
    plotFigure4()
    plotFigure5()
    # plotCorrelation()

if __name__ == '__main__':
    main()


