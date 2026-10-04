"""Explicit registered eye-opening traces and source topology domains.
The traces are separate from iris/brow/crease marks; no RGB-based deletion.
"""
import pathlib,json,numpy as np,collections,hashlib
from glb_io import read_glb
r=pathlib.Path(__file__).resolve().parents[1];src=r/'models/white_01_exact_duplicates.glb';j,b,a=read_glb(src);p=j['meshes'][0]['primitives'][0];P=a(p['attributes']['POSITION'])*j['nodes'][0]['scale']+j['nodes'][0]['translation'];N=a(p['attributes']['NORMAL']);UV=a(p['attributes']['TEXCOORD_0']);F=a(p['indices']).reshape(-1,3);C=P[F].mean(1);W,inv=np.unique(P,axis=0,return_inverse=True);WF=inv[F]
eye_data={
 'near':{'aperture':[[63,453],[82,441],[112,428],[146,420],[177,418],[212,423],[242,437],[257,456],[271,482],[250,493],[221,499],[184,499],[147,493],[111,483],[82,468]],'outer':[[35,447],[58,423],[99,402],[141,397],[186,397],[230,403],[260,424],[282,451],[295,489],[274,514],[227,525],[180,526],[132,518],[86,502],[51,478]]},
 'far':{'aperture':[[484,440],[494,412],[513,387],[540,365],[570,349],[602,339],[631,337],[656,343],[656,369],[642,392],[620,414],[591,430],[553,441],[516,446]],'outer':[[461,443],[468,407],[491,374],[523,345],[559,326],[597,315],[635,314],[674,326],[682,366],[666,408],[637,437],[601,458],[552,467],[502,468]]}}
def to_world(q):q=np.array(q,float);return np.c_[.009+(q[:,0]-400)*.2/800,.78-(q[:,1]-400)*.2/800]
def inside(points,poly):
 x=points[:,0];y=points[:,1];result=np.zeros(len(points),bool)
 for a0,b0 in zip(poly,np.roll(poly,-1,axis=0)):
  cond=(a0[1]>y)!=(b0[1]>y);cross=(b0[0]-a0[0])*(y-a0[1])/(b0[1]-a0[1]+1e-30)+a0[0];result^=cond&(x<cross)
 return result
reports={};arrays={};selected_sets=[]
for name,d in eye_data.items():
 aperture=to_world(d['aperture']);outer=to_world(d['outer']);select=inside(C[:,:2],outer)&(C[:,2]>.025)&(C[:,2]<.18);ids=np.flatnonzero(select);selected_sets.append(set(ids.tolist()));faces=WF[ids];_,unique_face=np.unique(np.sort(faces,axis=1),axis=0,return_index=True);faces=faces[np.sort(unique_face)];edges=collections.Counter(tuple(sorted((int(u),int(v))))for f in faces for u,v in zip(f,np.roll(f,-1)));bound=[e for e,n in edges.items()if n==1];adj=collections.defaultdict(list)
 for u,v in bound:adj[u].append(v);adj[v].append(u)
 bad={int(k):len(v)for k,v in adj.items()if len(v)!=2};loops=[]
 if not bad:
  pending=set(adj)
  while pending:
   start=min(pending);cur=start;previous=None;loop=[]
   while True:
    loop.append(cur);nxt=next(v for v in adj[cur]if v!=previous);previous,cur=cur,nxt
    if cur==start:break
    assert len(loop)<=len(adj)
   pending.difference_update(loop);loops.append(loop)
 areas=[float(abs(np.sum(W[q,0]*np.roll(W[q,1],-1)-np.roll(W[q,0],-1)*W[q,1]))/2)for q in loops]
 rep={'explicit_aperture_pixels':d['aperture'],'selection_guide_pixels':d['outer'],'selected_current_faces':len(ids),'selected_unique_geometry_faces':len(faces),'boundary_edges':len(bound),'boundary_bad_degree_vertices':bad,'boundary_loop_lengths':[len(x)for x in loops],'boundary_projected_areas':areas,'more_than_two_incident_selected_edges':sum(v>2 for v in edges.values()),'selected_depth_bounds':[float(P[F[ids],2].min()),float(P[F[ids],2].max())]};reports[name]=rep;arrays[name+'_selected_current_faces']=ids;arrays[name+'_aperture_xy']=aperture;arrays[name+'_outer_guide_xy']=outer
 for i,loop in enumerate(loops):arrays[f'{name}_boundary_{i}_position_ids']=np.array(loop);arrays[f'{name}_boundary_{i}_positions']=W[loop]
assert not(selected_sets[0]&selected_sets[1]);np.savez_compressed(r/'checks/white_eye_domains02.npz',**arrays);report={'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'exact_camera_metadata':'renders/white_01_eyes_front_pbr.json','eyes':reports,'status':'Unapproved explicit spatial/topology preparation. No model was changed. Boundary simplicity, aperture containment, retained-source ownership and tangent/depth continuity remain gates.'};(r/'checks/white_eye_domains02.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
