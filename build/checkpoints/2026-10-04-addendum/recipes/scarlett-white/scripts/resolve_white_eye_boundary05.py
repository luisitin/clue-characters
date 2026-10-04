"""Absorb only measured branch endpoints into bounded source eye domains.
Interfaces are selected-to-retained edges, not counts inside a nonmanifold patch.
"""
import pathlib,json,numpy as np,collections,hashlib
from glb_io import read_glb
r=pathlib.Path(__file__).resolve().parents[1];src=r/'models/white_01_exact_duplicates.glb';j,b,a=read_glb(src);p=j['meshes'][0]['primitives'][0];P=a(p['attributes']['POSITION'])*j['nodes'][0]['scale']+j['nodes'][0]['translation'];F=a(p['indices']).reshape(-1,3);C=P[F].mean(1);W,inv=np.unique(P,axis=0,return_inverse=True);WF=inv[F];d=np.load(r/'checks/white_eye_domains02.npz');initial={n:d[n+'_selected_current_faces']for n in ['near','far']};apertures={n:d[n+'_aperture_xy']for n in initial};guides={n:d[n+'_outer_guide_xy']for n in initial};d.close();all_edges=collections.defaultdict(set);vertex_faces=collections.defaultdict(set)
for fi,f in enumerate(WF):
 for u,v in zip(f,np.roll(f,-1)):all_edges[tuple(sorted((int(u),int(v))))].add(fi)
 for v in f:vertex_faces[int(v)].add(fi)
def inside(points,poly):
 x=points[:,0];y=points[:,1];result=np.zeros(len(points),bool)
 for aa,bb in zip(poly,np.roll(poly,-1,axis=0)):result^=((aa[1]>y)!=(bb[1]>y))&(x<(bb[0]-aa[0])*(y-aa[1])/(bb[1]-aa[1]+1e-30)+aa[0])
 return result
def distance(points,poly):
 dist=np.full(len(points),np.inf)
 for aa,bb in zip(poly,np.roll(poly,-1,axis=0)):
  v=bb-aa;t=np.clip((points-aa)@v/(v@v),0,1);dist=np.minimum(dist,np.linalg.norm(points-aa-t[:,None]*v,axis=1))
 return np.where(inside(points,poly),0,dist)
def interface(selected):
 edges={tuple(sorted((int(u),int(v))))for fi in selected for u,v in zip(WF[fi],np.roll(WF[fi],-1))};edges=[e for e in edges if all_edges[e]-selected];adj=collections.defaultdict(list)
 for u,v in edges:adj[u].append(v);adj[v].append(u)
 bad={k:len(v)for k,v in adj.items()if len(v)!=2};return edges,adj,bad
def find_loops(adj):
 pending=set(adj);loops=[]
 while pending:
  start=min(pending);cur=start;previous=None;loop=[]
  while True:
   loop.append(cur);nxt=next(v for v in adj[cur]if v!=previous);previous,cur=cur,nxt
   if cur==start:break
   assert len(loop)<=len(adj)
  pending.difference_update(loop);loops.append(loop)
 return loops
def projected_problems(loops):
 problems=set();witnesses=[]
 def cross(a,b):return a[0]*b[1]-a[1]*b[0]
 for loop in loops:
  n=len(loop);q=W[loop,:2]
  for i in range(n):
   a,b=q[i],q[(i+1)%n]
   if np.linalg.norm(b-a)<1e-6:problems.update([loop[i],loop[(i+1)%n]]);witnesses.append({'collapsed_edge':[loop[i],loop[(i+1)%n]]})
   for j in range(i+2,n):
    if i==0 and j==n-1:continue
    c,d=q[j],q[(j+1)%n]
    if cross(b-a,c-a)*cross(b-a,d-a)<-1e-20 and cross(d-c,a-c)*cross(d-c,b-c)<-1e-20:
     vs=[loop[i],loop[(i+1)%n],loop[j],loop[(j+1)%n]];problems.update(vs);witnesses.append({'projected_crossing':vs})
 return problems,witnesses
reports={};arrays={};domains=[]
for name,seed in initial.items():
 selected=set(seed.tolist());guide=guides[name];allowed=(distance(C[:,:2],guide)<.009)&(C[:,2]>.025)&(C[:,2]<.18);history=[]
 for iteration in range(12):
  edges,adj,bad=interface(selected);problems=set(bad);witnesses=[]
  if not bad:
   loops0=find_loops(adj);extra,witnesses=projected_problems(loops0);problems|=extra
  history.append({'iteration':iteration,'selected_faces':len(selected),'interface_edges':len(edges),'bad_degrees':{str(k):v for k,v in bad.items()},'projected_witnesses':witnesses})
  if not problems:break
  additions={fi for vi in problems for fi in vertex_faces[vi]if allowed[fi]}-selected
  if not additions:break
  selected|=additions
 edges,adj,bad=interface(selected);loops=[]
 if not bad:
  pending=set(adj)
  while pending:
   start=min(pending);cur=start;previous=None;loop=[]
   while True:
    loop.append(cur);nxt=next(v for v in adj[cur]if v!=previous);previous,cur=cur,nxt
    if cur==start:break
    assert len(loop)<=len(adj)
   pending.difference_update(loop);loops.append(loop)
 loop_areas=[float(abs(np.sum(W[q,0]*np.roll(W[q,1],-1)-np.roll(W[q,0],-1)*W[q,1]))/2)for q in loops];order=np.argsort(loop_areas)[::-1];loops=[loops[i]for i in order];loop_areas=[loop_areas[i]for i in order]
 reports[name]={'history':history,'selected_faces':len(selected),'added_branch_family_faces':len(selected)-len(seed),'interface_bad_degrees':{str(k):v for k,v in bad.items()},'loop_lengths':[len(q)for q in loops],'projected_loop_areas':loop_areas,'projected_boundary_problems':projected_problems(loops)[1],'maximum_centroid_guide_expansion_m':float(distance(C[list(selected),:2],guide).max())};arrays[name+'_selected_current_faces']=np.array(sorted(selected));arrays[name+'_aperture_xy']=apertures[name];domains.append(selected)
 for i,loop in enumerate(loops):arrays[f'{name}_boundary_{i}_position_ids']=np.array(loop);arrays[f'{name}_boundary_{i}_positions']=W[loop]
assert not(domains[0]&domains[1]);np.savez_compressed(r/'checks/white_eye_domains05.npz',**arrays);q={'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'eyes':reports,'status':'Unapproved bounded branch-resolution study, no model changed. Still requires simple projected domain, aperture containment, source perimeter/tangent evidence and exact geometry appearance.'};(r/'checks/white_eye_domains05.json').write_text(json.dumps(q,indent=2));print(q,flush=True)
