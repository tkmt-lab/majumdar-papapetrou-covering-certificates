from pathlib import Path
from fractions import Fraction as F
import itertools,json
P=Path(__file__).resolve().parent;g=json.loads((P/'geometry.json').read_text());result={'boxes':{},'pairwise_disjoint':{},'strips':{}}
def rat(x):return [str(x.numerator),str(x.denominator)]
for name,b in g['boxes'].items():
 c=list(map(F,b['center']));eu=list(map(F,b['eu']));es=list(map(F,b['es']));ru,rs=map(F,b['radius'])
 det=ru*rs*(eu[0]*es[1]-es[0]*eu[1]);assert det!=0
 vertices=[[c[i]+u*ru*eu[i]+s*rs*es[i] for i in range(2)] for u,s in itertools.product([-1,1],repeat=2)]
 qmin=min(v[0] for v in vertices);qmax=max(v[0] for v in vertices)
 result['boxes'][name]={'frame_determinant':rat(det),'vertices':[[rat(v) for v in point] for point in vertices],'q_projection':[rat(qmin),rat(qmax)]}
for a,b in itertools.combinations(g['boxes'],2):
 xa=[F(*map(int,x)) for x in result['boxes'][a]['q_projection']];xb=[F(*map(int,x)) for x in result['boxes'][b]['q_projection']]
 gap=max(xa[0]-xb[1],xb[0]-xa[1]);assert gap>0
 result['pairwise_disjoint'][a+b]={'positive_q_gap':rat(gap),'pass':True}
for edge,interval in g['strips'].items():
 lo,hi=map(F,interval.strip('[]').split(','));assert -1<lo<hi<1
 result['strips'][edge]={'u':[rat(lo),rat(hi)],'s':[['-1','1'],['1','1']]}
for source in ['O','B']:
 rows=sorted([v['u'] for k,v in result['strips'].items() if k[0]==source],key=lambda row:F(*map(int,row[0])))
 assert F(*map(int,rows[0][1]))<F(*map(int,rows[1][0]))
edges=[tuple(k.split('->')) for k in g['strips']];E=[[int(a[1]==b[0]) for b in edges] for a in edges]
# Positive eigenvector in Q(phi), phi^2=phi+1; pairs encode a+b*phi.
v={'O':(0,1),'A':(1,0),'B':(0,1)};w=[v[b] for a,b in edges]
for row,(a,b) in zip(E,w):
 lhs=tuple(sum(row[j]*w[j][k] for j in range(5)) for k in range(2));assert lhs==(b,a+b)
result['edge_order']=['->'.join(e) for e in edges];result['edge_matrix']=E
result['spectral_radius']={'value':'(1+sqrt(5))/2','positive_eigenvector_Qphi':w,'exact_eigenvector_check':True,'reason':'strictly positive eigenvector gives eigenvalue phi and induced weighted infinity norm phi; hence rho(E)=phi','entropy_bound':'conditional on all covering and first-return obligations: h_top(P)>=log(phi)'}
result['status']='PASS_EXACT_GEOMETRY_AND_CONDITIONAL_GRAPH_ONLY';result['return_map_or_C1_C2_proven']=False
(P/'geometry-check.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status']);print('edge_matrix',E)
