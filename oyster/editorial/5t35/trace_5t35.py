import numpy as np, json
from scipy.ndimage import gaussian_filter
from skimage import measure
import os
# Put 5t35.pdb (https://files.rcsb.org/download/5T35.pdb) next to this script, then run it.
D=os.path.dirname(os.path.abspath(__file__))+'/'
atoms={}; lig={}
for l in open(D+'5t35.pdb'):
    if l[:6] in ('ATOM  ','HETATM'):
        el=l[76:78].strip() or l[12:14].strip()[0]
        if el=='H': continue
        xyz=[float(l[30:38]),float(l[38:46]),float(l[46:54])]
        ch=l[21]
        if l[:4]=='ATOM': atoms.setdefault(ch,[]).append(xyz)
        elif l[17:20]=='759': lig.setdefault(ch,[]).append((xyz,el))
A={k:np.array(v) for k,v in atoms.items()}
L=np.array([a[0] for a in lig['D']]); Lel=[a[1] for a in lig['D']]
def mind(a,b): return min(np.min(np.linalg.norm(a[:,None,:]-b[None,::7,:],axis=2),axis=1))
print('lig(D) to A %.1f  to E %.1f  to D %.1f'%(mind(L,A['A']),mind(L,A['E']),mind(L,A['D'])))
groups={'target':A['A'],'e3':A['D'],'elo':np.vstack([A['B'],A['C']])}
allp=np.vstack(list(groups.values())+[L]); cen=allp.mean(0)
def rot(q):
    q=q/np.linalg.norm(q); w,x,y,z=q
    return np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
def masks(R,res=1.5):
    P={k:(v-cen)@R.T for k,v in groups.items()}
    allxy=np.vstack([p[:,:2] for p in P.values()]); mn=allxy.min(0)-6
    out={}
    for k,p in P.items():
        ij=((p[:,:2]-mn)/res).astype(int); g=np.zeros((int((allxy.max(0)-mn).max()/res)+12,)*2,bool)
        for di in (-1,0,1):
            for dj in (-1,0,1): g[np.clip(ij[:,0]+di,0,g.shape[0]-1),np.clip(ij[:,1]+dj,0,g.shape[1]-1)]=True
        out[k]=g
    return out
rng=np.random.default_rng(3); best=None
for i in range(2500):
    R=rot(rng.normal(size=4)); m=masks(R)
    ov=(m['target']&m['e3']).sum()+ (m['elo']&m['target']).sum()*1.5 + (m['elo']&m['e3']).sum()*.4
    tot=sum(v.sum() for v in m.values())
    score=ov/tot
    if best is None or score<best[0]: best=(score,R)
print('best overlap fraction %.3f'%best[0])
R=best[1]
groups2={'target':A['A'],'e3':A['D'],'eloc':A['C'],'elob':A['B']}
P={k:(v-cen)@R.T for k,v in groups2.items()}; PL=(L-cen)@R.T
# in-plane: target on the left, e3 on the right, elongins below
c=lambda k:P[k][:,:2].mean(0)
v=c('e3')-c('target'); ang=np.arctan2(v[1],v[0]); ca,sa=np.cos(-ang),np.sin(-ang); R2=np.array([[ca,-sa],[sa,ca]])
P2={k:p[:,:2]@R2.T for k,p in P.items()}; L2=PL[:,:2]@R2.T
if np.vstack([P2['eloc'],P2['elob']])[:,1].mean()<P2['target'][:,1].mean(): # SVG y grows downward: put elongins lower
    P2={k:p*[1,-1] for k,p in P2.items()}; L2=L2*[1,-1]
allxy=np.vstack(list(P2.values())); mid=(allxy.min(0)+allxy.max(0))/2; span=(allxy.max(0)-allxy.min(0)).max()
def norm(p): return (p-mid)/span
res=.5; mn=allxy.min(0)-8; shape=(np.ceil((allxy.max(0)-mn+8)/res)).astype(int)
out={'pdb':'5T35','span_A':round(float(span),1),'parts':{}}
for k,p in P2.items():
    g=np.zeros(shape[::-1]); ij=((p-mn)/res).astype(int); np.add.at(g,(ij[:,1],ij[:,0]),1)
    g=gaussian_filter(g,2.2/res)
    lv=g.max()*.06
    cs=measure.find_contours(g,lv); cs=sorted(cs,key=len,reverse=True)
    outer=measure.approximate_polygon(cs[0],tolerance=.9/res)[:-1]
    inner=[]
    for f in (.3,.52,.74):
        cc=[c for c in measure.find_contours(g,g.max()*f) if len(c)>30]
        cc=sorted(cc,key=len,reverse=True)[:2]
        inner+= [measure.approximate_polygon(c,tolerance=.9/res)[:-1] for c in cc]
    to=lambda c:[[round(float(x),4),round(float(y),4)] for x,y in norm(np.c_[c[:,1]*res+mn[0],c[:,0]*res+mn[1]])]
    out['parts'][k]={'outer':to(outer),'inner':[to(c) for c in inner]}
    print(k,'outer pts',len(outer),'inner',[len(c) for c in inner])
# ligand sticks
pts=norm(L2); bonds=[]
for i in range(len(L)):
    for j in range(i+1,len(L)):
        if np.linalg.norm(L[i]-L[j])<1.95: bonds.append([i,j])
out['ligand']={'atoms':[[round(float(x),4),round(float(y),4)] for x,y in pts],'el':Lel,'bonds':bonds}
json.dump(out,open(D+'5t35_shapes.json','w'))
print('ligand atoms',len(L),'bonds',len(bonds),'span',round(span,1))
