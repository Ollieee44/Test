"""The K48-linked tetraubiquitin chain for the click-through's tagging step, from its crystal structure.
Fits the 1UBQ ubiquitin (the mesh in meshes.json, centred on its atoms' mean) onto each subunit of PDB 2O6V (chains A-D,
A proximal: its Gly76 free to attach to the target; D distal), and writes each subunit's pose relative to the proximal one
(quaternion x y z w, translation in angstroms) and the proximal Gly76 carbonyl C, the point that joins the target.
Usage: python ub_chain.py 1ubq.pdb 2O6V.pdb ../ubchain.json   (both from files.rcsb.org/download/<id>.pdb)"""
import numpy as np, json, sys
def read(f):
    out=[]
    for l in open(f):
        if l.startswith(('ATOM','HETATM')) and l[16] in ' A':
            out.append((l[21], int(l[22:26]), l[12:16].strip(), np.array([float(l[30:38]),float(l[38:46]),float(l[46:54])]), l[:6]))
    return out
U=read(sys.argv[1])
mean=np.array([a[3] for a in U if a[4]=='ATOM  ']).mean(0)
ca1={a[1]:a[3]-mean for a in U if a[2]=='CA' and a[4]=='ATOM  '}
g76=[a[3] for a in U if a[1]==76 and a[2]=='C'][0]-mean
k48=[a[3] for a in U if a[1]==48 and a[2]=='NZ'][0]-mean
T=read(sys.argv[2])
def kabsch(P,Q):
    pc,qc=P.mean(0),Q.mean(0); H=(P-pc).T@(Q-qc); U_,S,Vt=np.linalg.svd(H); d=np.sign(np.linalg.det(Vt.T@U_.T))
    R=Vt.T@np.diag([1,1,d])@U_.T; return R, qc-R@pc
poses=[]
for ch in 'ABCD':
    ca={a[1]%100:a[3] for a in T if a[0]==ch and a[2]=='CA'}
    ks=[k for k in ca if k in ca1 and k<=72]
    P=np.array([ca1[k] for k in ks]); Q=np.array([ca[k] for k in ks]); R,t=kabsch(P,Q)
    print(ch,len(ks),'rmsd %.2f'%np.sqrt(((P@R.T+t-Q)**2).sum(1).mean())); poses.append((R,t))
R0,t0=poses[0]; rel=[(R0.T@R, R0.T@(t-t0)) for R,t in poses]
for i in range(3):
    a=rel[i][0]@k48+rel[i][1]; b=rel[i+1][0]@g76+rel[i+1][1]; print('link',i,'%.1f A'%np.linalg.norm(a-b))
def quat(R):
    w=np.sqrt(max(0,1+R[0,0]+R[1,1]+R[2,2]))/2; x=np.sqrt(max(0,1+R[0,0]-R[1,1]-R[2,2]))/2; y=np.sqrt(max(0,1-R[0,0]+R[1,1]-R[2,2]))/2; z=np.sqrt(max(0,1-R[0,0]-R[1,1]+R[2,2]))/2
    return [float(np.copysign(x,R[2,1]-R[1,2])),float(np.copysign(y,R[0,2]-R[2,0])),float(np.copysign(z,R[1,0]-R[0,1])),float(w)]
cent=np.mean([t for R,t in rel],0)
print('dist from g76', [round(float(np.linalg.norm(t-g76)),1) for R,t in rel], 'centroid-g', np.round(cent-g76,1), np.linalg.norm(cent-g76))
out={'g':[round(float(v),2) for v in g76],'poses':[[round(v,4) for v in quat(R)]+[round(float(v),2) for v in t] for R,t in rel]}
json.dump(out,open(sys.argv[3],'w')); print(json.dumps(out))
