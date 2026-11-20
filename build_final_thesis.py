"""
论文一体化生成 — 纯 python-docx API，零 XML hack。
按模板格式从头构建：封面→声明→摘要→目录→正文5章→结论→参考文献→附录→致谢
图片在正确位置内联插入。
"""
import os, json, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats
import joblib
warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

OUT = "北京市气候健康风险预警—智能体可视化平台_毕业论文.docx"
CD = "output/charts"
os.makedirs(CD, exist_ok=True)

doc = Document()

# ── 样式 ──────────────────────────────────────────
S = doc.styles['Normal']
S.font.name = '宋体'; S.font.size = Pt(12)
S.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
S.paragraph_format.line_spacing = Pt(20)
S.paragraph_format.first_line_indent = Cm(0.74)
for sec in doc.sections:
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.5); sec.bottom_margin = Cm(2.5)
    sec.left_margin = Cm(3.0); sec.right_margin = Cm(2.5)
for i in range(1,4):
    h = doc.styles[f'Heading {i}']
    h.font.name = '黑体'; h.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    h.font.color.rgb = RGBColor(0,0,0)
    h.paragraph_format.line_spacing = Pt(20)
    h.paragraph_format.first_line_indent = Cm(0)
H1 = doc.styles['Heading 1']; H1.font.size = Pt(16)
H1.paragraph_format.space_before = Pt(18); H1.paragraph_format.space_after = Pt(30)
H1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
H2 = doc.styles['Heading 2']; H2.font.size = Pt(14)
H2.paragraph_format.space_before = Pt(6); H2.paragraph_format.space_after = Pt(6)
H3 = doc.styles['Heading 3']; H3.font.size = Pt(12)
H3.paragraph_format.space_before = Pt(6); H3.paragraph_format.space_after = Pt(6)

# ── Helper ────────────────────────────────────────
def P(text, bold=False, al=None, fn='宋体', fs=Pt(12), ind=Cm(0.74), sb=0, sa=0):
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = Pt(20)
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.first_line_indent = ind
    if al is not None: p.paragraph_format.alignment = al
    r = p.add_run(text); r.font.name = fn
    r._element.rPr.rFonts.set(qn('w:eastAsia'), fn); r.font.size = fs; r.bold = bold
    return p

def H(text, level=1):
    if level == 1: doc.add_page_break()
    return doc.add_heading(text, level=level)

def IMG(path, caption, w=5.8):
    p = doc.add_paragraph(); p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(3)
    p.add_run().add_picture(path, width=Inches(w))
    p2 = doc.add_paragraph(); p2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.first_line_indent = Cm(0)
    p2.paragraph_format.space_before = Pt(3); p2.paragraph_format.space_after = Pt(6)
    r2 = p2.add_run(caption); r2.font.name = '宋体'
    r2._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体'); r2.font.size = Pt(10.5)
    return p2

# ── 预生成全部图表 ────────────────────────────────
print("Generating 11 charts...")
weather = pd.read_csv('output/weather_standard.csv', encoding='utf-8-sig')
disease = pd.read_csv('output/disease_standard.csv', encoding='utf-8-sig')
weather['date'] = pd.to_datetime(weather['date'], format='mixed')
disease['date'] = pd.to_datetime(disease['year'].astype(str)+'-'+disease['month'].astype(str)+'-01')
with open('models/model_ranking.json') as f: mr = json.load(f)
model = joblib.load('models/best_model.pkl')
train = pd.read_csv('models/train_split.csv'); test = pd.read_csv('models/test_split.csv')
fc = [c for c in train.columns if c != '__target__']
Xt = test[fc].values; yt = test['__target__'].values
vm = ~np.isnan(yt); Xt, yt = Xt[vm], yt[vm]; yp = model.predict(Xt)

# C1: 气象时序
fig, axes = plt.subplots(2,2,figsize=(12,8))
for i,d in enumerate(['海淀','朝阳','北京']):
    s = weather[weather['district']==d].sort_values('date').tail(100)
    axes[0,0].plot(s['date'],s['temp_avg'],color=['#2196F3','#FF9800','#4CAF50'][i],alpha=0.7,lw=1)
    axes[0,1].plot(s['date'],s['humidity_avg'],color=['#2196F3','#FF9800','#4CAF50'][i],alpha=0.7,lw=1)
    axes[1,0].bar(s['date'],s['precipitation'].fillna(0),color=['#2196F3','#FF9800','#4CAF50'][i],alpha=0.5,width=1)
    axes[1,1].plot(s['date'],s['wind_speed_avg'],color=['#2196F3','#FF9800','#4CAF50'][i],alpha=0.7,lw=1)
axes[0,0].set_title('日均气温 (°C)',fontsize=11,fontweight='bold')
axes[0,1].set_title('日均相对湿度 (%)',fontsize=11,fontweight='bold')
axes[1,0].set_title('日降水量 (mm)',fontsize=11,fontweight='bold')
axes[1,1].set_title('日均风速 (m/s)',fontsize=11,fontweight='bold')
for ax in axes.flat: ax.tick_params(labelsize=8); ax.xaxis.set_major_locator(ticker.MaxNLocator(6))
fig.autofmt_xdate(rotation=30,ha='right')
fig.legend(['海淀','朝阳','北京'],loc='upper center',ncol=3,fontsize=9,bbox_to_anchor=(0.5,1.02))
fig.suptitle('图3-2  北京市主要行政区气象要素时序对比',fontsize=13,fontweight='bold',y=1.03)
plt.tight_layout(); plt.savefig(f'{CD}/c1.png',dpi=200,bbox_inches='tight'); plt.close()
print("  [1/11] Weather timeseries ✓")

# C2: 相关性热力图
cc = ['temp_avg','temp_max','temp_min','humidity_avg','precipitation','wind_speed_avg','pressure_avg']
cr = weather[cc].dropna().corr()
fig,ax=plt.subplots(figsize=(8,6.5))
im=ax.imshow(cr.values,cmap='RdBu_r',vmin=-1,vmax=1,aspect='auto')
lbs=['气温','最高温','最低温','湿度','降水量','风速','气压']
ax.set_xticks(range(7)); ax.set_yticks(range(7))
ax.set_xticklabels(lbs,fontsize=9); ax.set_yticklabels(lbs,fontsize=9)
plt.setp(ax.get_xticklabels(),rotation=45,ha='right')
for i in range(7):
    for j in range(7):
        ax.text(j,i,f'{cr.values[i,j]:.2f}',ha='center',va='center',fontsize=8,
                color='white' if abs(cr.values[i,j])>0.5 else 'black')
cb=plt.colorbar(im,ax=ax,shrink=0.8); cb.set_label('相关系数',fontsize=9)
ax.set_title('图3-3  气象要素间皮尔逊相关系数热力图',fontsize=13,fontweight='bold',pad=12)
plt.tight_layout(); plt.savefig(f'{CD}/c2.png',dpi=200,bbox_inches='tight'); plt.close()
print("  [2/11] Correlation heatmap ✓")

# C3: 架构图
fig,ax=plt.subplots(figsize=(12,7)); ax.set_xlim(0,12); ax.set_ylim(0,7); ax.axis('off')
for i,(name,y,desc) in enumerate([
    ('展现层',5.5,'Streamlit Web UI\n├ 首页仪表板  ├ 数据采集/管理\n├ 数据可视化  ├ 建模训练/评测\n├ 报告生成      └ AI助手'),
    ('业务层',3.5,'AgentPipeline 调度引擎\n├ CrawlAgent → CleanAgent → FeatureEngineer\n├ ModelAgent → EvalAgent → ReportAgent\n└ ProvenanceTracker 溯源追踪'),
    ('计算层',1.5,'核心算法层\n├ 特征工程 (Lag/Rolling/OneHot)  ├ 10模型池\n├ 7指标评测 + 过拟合检测       ├ SHAP分析\n└ Jinja2 报告自动渲染'),
    ('数据层',-0.5,'多源数据接入层\n├ CMA地面观测 ┄ 高空探空  ├ 天气网 ┄ 天气后报网\n├ 北京市卫健委 ┄ 中国CDC     └ 文献 PDF/Excel 提取')]):
    ax.add_patch(plt.Rectangle((0,y),12,1.8,facecolor=['#667eea','#764ba2','#f093fb','#f5576c'][i],alpha=0.12,edgecolor=['#667eea','#764ba2','#f093fb','#f5576c'][i],lw=2))
    ax.text(0.2,y+1.55,name,fontsize=13,fontweight='bold',color=['#667eea','#764ba2','#f093fb','#f5576c'][i],va='top')
    ax.text(6,y+0.9,desc,fontsize=8,ha='center',va='center',family='monospace',bbox=dict(boxstyle='round,pad=0.5',facecolor='white',alpha=0.85))
for i in range(3): ax.annotate('',xy=(6,5.5-i*2-1.8),xytext=(6,5.5-i*2),arrowprops=dict(arrowstyle='->',color='#333',lw=2.5))
ax.set_title('图3-1  系统四层总体架构示意图',fontsize=15,fontweight='bold',y=1.02)
plt.tight_layout(); plt.savefig(f'{CD}/c3.png',dpi=200,bbox_inches='tight'); plt.close()
print("  [3/11] Architecture ✓")

# C4: 疾病趋势
td=disease.groupby('district')['incidence'].mean().nlargest(5).index.tolist()
fig,ax=plt.subplots(figsize=(10,5))
for i,d in enumerate(td):
    s=disease[disease['district']==d].sort_values('date')
    ax.plot(s['date'],s['incidence'],'o-',color=['#E53935','#1E88E5','#43A047','#FB8C00','#8E24AA'][i],markersize=4,lw=1.5,alpha=0.8,label=d)
ax.set_xlabel('日期',fontsize=10); ax.set_ylabel('发病率 (每10万人)',fontsize=10)
ax.set_title('图5-1  北京市主要行政区流感发病率时序趋势',fontsize=13,fontweight='bold')
ax.legend(loc='upper left',fontsize=8,ncol=3); ax.grid(True,alpha=0.3)
fig.autofmt_xdate(rotation=30,ha='right')
plt.tight_layout(); plt.savefig(f'{CD}/c4.png',dpi=200,bbox_inches='tight'); plt.close()
print("  [4/11] Disease trend ✓")

# C5: 季节性热力图
dp=disease.pivot_table(values='incidence',index='district',columns='month',aggfunc='mean')
fig,ax=plt.subplots(figsize=(10,6))
im=ax.imshow(dp.values,cmap='YlOrRd',aspect='auto')
ax.set_xticks(range(12)); ax.set_xticklabels([f'{m}月' for m in range(1,13)],fontsize=9)
ax.set_yticks(range(len(dp.index))); ax.set_yticklabels(dp.index,fontsize=9)
for i in range(len(dp.index)):
    for j in range(12):
        v=dp.values[i,j]
        if not np.isnan(v): ax.text(j,i,f'{v:.0f}',ha='center',va='center',fontsize=7,color='white' if v>np.nanmean(dp.values) else 'black')
cb=plt.colorbar(im,ax=ax,shrink=0.8); cb.set_label('平均发病率 (每10万人)',fontsize=9)
ax.set_title('图5-2  北京市各行政区逐月流感发病率季节性热力图',fontsize=13,fontweight='bold',pad=12)
plt.tight_layout(); plt.savefig(f'{CD}/c5.png',dpi=200,bbox_inches='tight'); plt.close()
print("  [5/11] Seasonal heatmap ✓")

# C6: 北京地图
dc={'海淀':(116.30,39.96),'朝阳':(116.44,39.92),'北京':(116.41,39.90),'丰台':(116.29,39.86),'石景山':(116.22,39.91),'通州':(116.66,39.90),'顺义':(116.65,40.13),'大兴':(116.34,39.73),'昌平':(116.23,40.22),'房山':(116.14,39.75),'门头沟':(116.10,39.94),'密云':(116.84,40.37),'怀柔':(116.63,40.32),'平谷':(117.12,40.14),'延庆':(115.97,40.46)}
da=weather.groupby('district')['temp_avg'].mean().reset_index()
dpairs=[(r['district'],round(r['temp_avg'],1)) for _,r in da.iterrows() if r['district'] in dc]
fig,ax=plt.subplots(figsize=(8,7))
xs,ys,vs=[dc[d][0] for d,_ in dpairs],[dc[d][1] for d,_ in dpairs],[v for _,v in dpairs]
sc=ax.scatter(xs,ys,c=vs,s=[abs(v)*8 for v in vs],cmap='YlOrRd',edgecolors='black',lw=0.5,alpha=0.8)
for d,v in dpairs: ax.annotate(f'{d}\n{v}°C',dc[d],fontsize=7,ha='center',va='bottom',xytext=(0,8),textcoords='offset points')
ax.set_xlim(115.6,117.4); ax.set_ylim(39.5,40.7)
ax.set_xlabel('经度 (°E)',fontsize=10); ax.set_ylabel('纬度 (°N)',fontsize=10)
cb=plt.colorbar(sc,ax=ax); cb.set_label('平均气温 (°C)',fontsize=9)
ax.set_title('图5-3  北京市各行政区平均气温空间分布',fontsize=13,fontweight='bold')
plt.tight_layout(); plt.savefig(f'{CD}/c6.png',dpi=200,bbox_inches='tight'); plt.close()
print("  [6/11] Beijing map ✓")

# C7: 模型排名
am=mr.get('all_models',[]); ms=sorted(am,key=lambda x:x.get('score',0),reverse=True)
nm=[m['name'] for m in ms]; cb7=['#1a237e' if n=='lightgbm' else '#bbdefb' for n in nm]
fig,axes=plt.subplots(1,3,figsize=(14,5))
for ai,(metric,title,fmt) in enumerate([([m['r2'] for m in ms],'R²','.3f'),([m['rmse'] for m in ms],'RMSE','.1f'),([m['mape'] for m in ms],'MAPE (%)','.1f')]):
    axes[ai].barh(nm[::-1],metric[::-1],color=cb7[::-1],edgecolor='white')
    axes[ai].set_xlabel(title,fontsize=10); axes[ai].set_title(title,fontsize=11,fontweight='bold')
    for j,v in enumerate(metric[::-1]): axes[ai].text(v+(0.01 if ai==0 else max(metric)*0.02),j,f'{v:{fmt}}',va='center',fontsize=8)
fig.suptitle('图5-4  十种机器学习模型性能对比',fontsize=14,fontweight='bold',y=1.02)
plt.tight_layout(); plt.savefig(f'{CD}/c7.png',dpi=200,bbox_inches='tight'); plt.close()
print("  [7/11] Model ranking ✓")

# C8: 雷达图
t5=ms[:5]; mrl=['R²','Adj R²','1-MAPE','CV R² Mean','Score']
ang=np.linspace(0,2*np.pi,len(mrl),endpoint=False).tolist(); ang+=ang[:1]
fig,ax=plt.subplots(figsize=(7,7),subplot_kw=dict(polar=True))
rc8=['#E53935','#1E88E5','#43A047','#FB8C00','#8E24AA']
for i,m in enumerate(t5):
    vs=[m['r2'],m.get('adj_r2',m['r2']-0.01),1-m['mape']/100,m.get('cv_r2_mean',m['r2']),m.get('score',0)]; vs+=vs[:1]
    ax.fill(ang,vs,alpha=0.1,color=rc8[i]); ax.plot(ang,vs,'o-',lw=2,color=rc8[i],label=m['name'],markersize=4)
ax.set_xticks(ang[:-1]); ax.set_xticklabels(mrl,fontsize=10); ax.set_ylim(0,1.05)
ax.set_title('图5-5  最优五模型多维度雷达对比图',fontsize=13,fontweight='bold',pad=20)
ax.legend(loc='upper right',bbox_to_anchor=(1.25,1.1),fontsize=9)
plt.tight_layout(); plt.savefig(f'{CD}/c8.png',dpi=200,bbox_inches='tight'); plt.close()
print("  [8/11] Radar chart ✓")

# C9: 预测vs实测
r2=mr['metrics']['r2']; rmse=mr['metrics']['rmse']; mae=mr['metrics']['mae']
fig,ax=plt.subplots(figsize=(7,6.5))
ax.scatter(yt,yp,alpha=0.5,s=30,c='#2196F3',edgecolors='white',lw=0.3)
mv,Mv=min(yt.min(),yp.min())*0.95,max(yt.max(),yp.max())*1.05
ax.plot([mv,Mv],[mv,Mv],'--',color='red',lw=1.5,alpha=0.7,label='理想拟合线')
ax.set_xlim(mv,Mv); ax.set_ylim(mv,Mv)
ax.set_xlabel('实测发病率',fontsize=11); ax.set_ylabel('预测发病率',fontsize=11)
ax.set_title('图5-6  LightGBM模型预测值与实测发病率拟合散点图',fontsize=13,fontweight='bold')
ax.legend(fontsize=9)
ax.text(0.05,0.95,f'R² = {r2:.4f}\nRMSE = {rmse:.2f}\nMAE = {mae:.2f}',transform=ax.transAxes,fontsize=10,verticalalignment='top',bbox=dict(boxstyle='round,pad=0.5',facecolor='lightyellow',alpha=0.8))
ax.grid(True,alpha=0.3)
plt.tight_layout(); plt.savefig(f'{CD}/c9.png',dpi=200,bbox_inches='tight'); plt.close()
print("  [9/11] Pred vs actual ✓")

# C10: 残差诊断
res=yt-yp
fig,axes=plt.subplots(1,2,figsize=(12,5))
axes[0].scatter(yp,res,alpha=0.5,s=30,c='#FF9800',edgecolors='white',lw=0.3)
axes[0].axhline(y=0,color='red',linestyle='--',lw=1.5,alpha=0.7)
axes[0].axhline(y=np.std(res)*2,color='gray',linestyle=':',lw=1,alpha=0.5,label='±2σ')
axes[0].axhline(y=-np.std(res)*2,color='gray',linestyle=':',lw=1,alpha=0.5)
axes[0].set_xlabel('预测值',fontsize=10); axes[0].set_ylabel('残差',fontsize=10)
axes[0].set_title('残差 vs 预测值（方差齐性检验）',fontsize=11,fontweight='bold')
axes[0].legend(fontsize=8); axes[0].grid(True,alpha=0.3)
stats.probplot(res,dist="norm",plot=axes[1])
axes[1].get_lines()[0].set_markerfacecolor('#2196F3'); axes[1].get_lines()[0].set_markeredgecolor('white')
axes[1].get_lines()[0].set_alpha(0.5); axes[1].get_lines()[1].set_color('red'); axes[1].get_lines()[1].set_linestyle('--')
axes[1].set_title('残差 Q-Q 正态性检验',fontsize=11,fontweight='bold')
fig.suptitle('图5-7  残差诊断分析',fontsize=14,fontweight='bold',y=1.02)
plt.tight_layout(); plt.savefig(f'{CD}/c10.png',dpi=200,bbox_inches='tight'); plt.close()
print("  [10/11] Residual diagnosis ✓")

# C11: SHAP
fi=mr.get('feature_importance',{})
fs=sorted(fi.items(),key=lambda x:x[1],reverse=True)[:15]
fn=[n for n,v in fs]; fv=[v for n,v in fs]
fig,ax=plt.subplots(figsize=(9,5.5))
cfi=['#1a237e' if 'temp_avg_roll3_std' in n else '#5c6bc0' if v>0 else '#e0e0e0' for n,v in fs]
bars=ax.barh(fn[::-1],fv[::-1],color=cfi[::-1])
ax.set_xlabel('SHAP重要性得分',fontsize=11)
ax.set_title('图5-8  LightGBM模型SHAP特征重要性排序（前15位）',fontsize=13,fontweight='bold')
for bar,(name,val) in zip(bars,fs[::-1]):
    if val>0: ax.text(val+5,bar.get_y()+bar.get_height()/2,f'{val:.0f}',va='center',fontsize=8)
ax.grid(True,alpha=0.2,axis='x')
plt.tight_layout(); plt.savefig(f'{CD}/c11.png',dpi=200,bbox_inches='tight'); plt.close()
print("  [11/11] SHAP ✓\n")

# ═══════════════════════════════════════════════════════
#  封面
# ═══════════════════════════════════════════════════════
for _ in range(6): P("",ind=Cm(0))
P("本科生毕业设计(论文)",bold=True,al=WD_ALIGN_PARAGRAPH.CENTER,fn='黑体',fs=Pt(22),ind=Cm(0),sa=30)
P("北京市气候健康风险预警\n——智能体可视化平台的设计与实现",bold=True,al=WD_ALIGN_PARAGRAPH.CENTER,fn='黑体',fs=Pt(22),ind=Cm(0),sa=60)
for line in ["姓    名：________________________","学    号：________________________",
             "学    院：数学与数据科学系","专业(方向)：信息与计算科学",
             "班    级：________________________","指导教师：何黎黎"]:
    P(line,al=WD_ALIGN_PARAGRAPH.CENTER,ind=Cm(0),fs=Pt(14))
P("",ind=Cm(0)); P("2026年7月",al=WD_ALIGN_PARAGRAPH.CENTER,ind=Cm(0),fs=Pt(14))

# ═══════════════════════════════════════════════════════
#  创见性声明
# ═══════════════════════════════════════════════════════
doc.add_page_break(); H("创见性声明",1)
P("本人声明：所呈交的毕业设计（论文）是本人在指导教师的指导下进行的工作和取得的成果，"
  "符合学校及学院的毕业设计（论文）管理规定，论文中所引用的他人已经发表或撰写过的研究成果，"
  "均加以特别标注并在此表示致谢。与我一同工作的同志对本论文所做的任何贡献也已在论文中作了"
  "明确的说明并表示谢意。")
P(""); P(""); P("毕业论文作者签名：         签字日期：     年  月  日",ind=Cm(0))

# ═══════════════════════════════════════════════════════
#  版权使用授权书
# ═══════════════════════════════════════════════════════
doc.add_page_break(); H("本科毕业设计（论文）版权使用授权书",1)
P("本毕业设计（论文）作者完全了解北京建筑大学有关保留、使用毕业设计（论文）的规定。"
  "特授权北京建筑大学可以将毕业设计（论文）的全部或部分内容编入有关数据库进行检索，"
  "并采用影印、缩印或扫描等复制手段保存、汇编以供查阅和借阅。同意学校向国家有关部门"
  "或机构送交毕业设计（论文）的复印件和磁盘。")
P("（保密的毕业论文在解密后适用本授权说明）"); P(""); P("")
P("毕业论文作者签名：           指导教师签名：",ind=Cm(0)); P("")
P("签字日期：     年  月  日    签字日期：    年  月  日",ind=Cm(0))

# ═══════════════════════════════════════════════════════
#  中文摘要
# ═══════════════════════════════════════════════════════
doc.add_page_break(); P("",ind=Cm(0))
P("摘    要",bold=True,al=WD_ALIGN_PARAGRAPH.CENTER,fn='黑体',fs=Pt(16),ind=Cm(0),sb=18,sa=30)
P("在全球气候变化的背景下，极端天气事件频发，气候因素对人体健康的影响日益显著。"
  "北京市作为超大型城市，人口密集、环境复杂，气候敏感性疾病（如流感、心脑血管疾病等）"
  "的发病风险与气象要素之间存在复杂的非线性关联。传统的气象-健康分析依赖人工采集数据"
  "和单一统计模型，存在数据来源单一、处理效率低、模型泛化能力不足等问题。\n\n"
  "本文设计并实现了一套基于智能体架构的北京市气候健康风险预警可视化平台。"
  "该平台集成了多源气象数据自动采集、自适应数据清洗与质控、特征工程自动化、"
  "多模型自适应建模、全维度模型评测以及智能报告生成六大核心功能模块。"
  "在数据采集层，系统通过爬虫引擎对接国家气象信息中心地面与高空气象观测数据、"
  "中国天气网历史数据、北京市卫健委疾病监测数据等七个数据源；"
  "在数据清洗层，实现了自适应缺失值处理、异常值检测、单位标准化和哨兵值识别等质控机制；"
  "在建模层，构建了包含LightGBM、XGBoost、随机森林、支持向量回归等十种机器学习模型的"
  "自适应对比框架，引入RFE特征筛选、5折交叉验证和网格搜索超参数优化。\n\n"
  "实验结果表明，LightGBM模型在北京市气象-疾病关联预测中表现最优，测试集R²达0.987，"
  "RMSE为46.51，MAPE为7.68%，且未出现过拟合或欠拟合。温度滚动标准差、温度滑动均值"
  "和月份周期性特征为最重要的预测因子。平台采用Streamlit框架构建Web交互界面，"
  "通过AgentPipeline配置驱动引擎实现全流程无人自动化调度，并集成大语言模型AI助手"
  "提供智能问答与辅助分析功能。该平台为北京市气候敏感性疾病的风险预警提供了"
  "一套高效、可扩展的技术解决方案。")
P(""); P("关键词：气候健康；风险预警；机器学习；智能体；数据可视化")

# ═══════════════════════════════════════════════════════
#  英文摘要
# ═══════════════════════════════════════════════════════
doc.add_page_break(); P("",ind=Cm(0))
P("ABSTRACT",bold=True,al=WD_ALIGN_PARAGRAPH.CENTER,fn='Times New Roman',fs=Pt(16),ind=Cm(0),sb=18,sa=30)
P("Against the backdrop of global climate change, extreme weather events occur frequently, "
  "and the impact of climatic factors on human health has become increasingly significant. "
  "As a megacity with dense population and complex environment, Beijing faces complex nonlinear "
  "associations between the risk of climate-sensitive diseases (such as influenza and "
  "cardiovascular diseases) and meteorological elements. Traditional meteorological-health "
  "analysis relies on manual data collection and single statistical models, suffering from "
  "limited data sources, low processing efficiency, and insufficient model generalization.\n\n"
  "This thesis designs and implements an agent-based visualization platform for climate health "
  "risk early warning in Beijing. The platform integrates six core functional modules: "
  "multi-source meteorological data automatic collection, adaptive data cleaning and quality "
  "control, automated feature engineering, multi-model adaptive modeling, comprehensive model "
  "evaluation, and intelligent report generation. At the data collection layer, the system "
  "connects to seven data sources including CMA surface and upper-air observations, historical "
  "weather data from Weather.com, and disease surveillance data from Beijing Municipal Health "
  "Commission. At the data cleaning layer, adaptive mechanisms for missing value processing, "
  "outlier detection, unit standardization, and sentinel value identification are implemented. "
  "At the modeling layer, an adaptive comparison framework incorporating ten machine learning "
  "models—including LightGBM, XGBoost, Random Forest, and Support Vector Regression—is "
  "constructed, with RFE feature selection, 5-fold cross-validation, and grid search "
  "hyperparameter optimization.\n\n"
  "Experimental results demonstrate that the LightGBM model performs optimally in predicting "
  "the meteorological-disease association in Beijing, achieving an R² of 0.987, RMSE of "
  "46.51, and MAPE of 7.68% on the test set, with no overfitting or underfitting detected. "
  "Temperature rolling standard deviation, temperature moving average, and monthly cyclical "
  "features emerged as the most important predictors. The platform employs the Streamlit "
  "framework for its web interface, utilizes the AgentPipeline configuration-driven engine "
  "for fully automated unattended scheduling, and integrates a large language model AI "
  "assistant for intelligent Q&A and auxiliary analysis. This platform provides an efficient "
  "and scalable technical solution for climate-sensitive disease risk early warning in Beijing.",
  fn='Times New Roman',fs=Pt(12))
P(""); P("Key Words: climate health; risk early warning; machine learning; intelligent agent; "
  "data visualization",fn='Times New Roman',fs=Pt(12))

print("Cover + Abstracts done. Building main body...")
doc.save(OUT)
print(f"Phase 1 saved ({os.path.getsize(OUT)/1024:.0f} KB). Continuing with chapters...")
