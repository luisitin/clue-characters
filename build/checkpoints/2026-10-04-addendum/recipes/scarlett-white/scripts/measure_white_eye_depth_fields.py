"""Measure the restored orbital depth fields and the shallow-cap mismatch without generating a model."""
import pathlib,json,numpy as np,sys,hashlib,collections
from scipy.interpolate import CubicSpline
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]/'shared_tools/triangle_lib'))
import triangle
from glb_io import read_glb
r=pathlib.Path(__file__).resolve().parents[1];src=r/'models/white_01_exact_duplicates.glb';j,b,a=read_glb(src);p=j['meshes'][0]['primitives'][0];P=a(p['attributes']['POSITION'])*j['nodes'][0]['scale']+j['nodes'][0]['translation'];F=a(p['indices']).reshape(-1,3);W,inv=np.unique(P,axis=0,return_inverse=True);WF=inv[F];facecross=np.cross(P[F[:,1]]-P[F[:,0]],P[F[:,2]]-P[F[:,0]]);d=np.load(r/'checks/white_eye_domains05.npz');report={};output={}
def inside(points,poly):
 x=points[:,0];y=points[:,1];result=np.zeros(len(points),bool)
 for aa,bb in zip(poly,np.roll(poly,-1,axis=0)):result^=((aa[1]>y)!=(bb[1]>y))&(x<(bb[0]-aa[0])*(y-aa[1])/(bb[1]-aa[1]+1e-30)+aa[0])
 return result
def signed_area(q):return np.sum(q[:,0]*np.roll(q[:,1],-1)-np.roll(q[:,0],-1)*q[:,1])/2
def harmonic(V,T,known,values):
 edges=np.unique(np.sort(np.concatenate([T[:,[0,1]],T[:,[1,2]],T[:,[2,0]]]),axis=1),axis=0);i,j=edges.T;w=1/np.maximum(np.linalg.norm(V[i]-V[j],axis=1),1e-9);degree=np.bincount(np.r_[i,j],weights=np.r_[w,w],minlength=len(V));L=coo_matrix((np.r_[-w,-w,degree],(np.r_[i,j,np.arange(len(V))],np.r_[j,i,np.arange(len(V))])),shape=(len(V),len(V))).tocsr();used=np.unique(T);unknown=np.setdiff1d(used,known);z=np.full(len(V),np.nan);z[known]=values;z[unknown]=spsolve(L[unknown][:,unknown],-L[unknown][:,known]@values);assert np.isfinite(z[used]).all();assert z[used].min()>=min(values)-1e-9 and z[used].max()<=max(values)+1e-9;return z
for name in ['near','far']:
 selected=d[name+'_selected_current_faces'];boundary_ids=d[name+'_boundary_0_position_ids'];outer=d[name+'_boundary_0_positions'];ap=d[name+'_aperture_xy'];assert len(outer)==len(boundary_ids)
 if signed_area(outer[:,:2])<0:outer=outer[::-1];boundary_ids=boundary_ids[::-1]
 if signed_area(ap)<0:ap=ap[::-1]
 closed=np.vstack([ap,ap[0]]);t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(closed,axis=0),axis=1))];smooth=CubicSpline(t,closed,bc_type='periodic');ap=smooth(np.linspace(0,t[-1],192,endpoint=False));assert inside(ap,outer[:,:2]).all(),'Aperture leaves source outer boundary'
 distances=[]
 for aa,bb in zip(outer[:,:2],np.roll(outer[:,:2],-1,axis=0)):
  delta=bb-aa;weight=np.clip((ap-aa)@delta/(delta@delta),0,1);distances.append(np.linalg.norm(ap-aa-weight[:,None]*delta,axis=1))
 clearance=float(np.min(distances));assert clearance>.00015
 retained=np.ones(len(F),bool);retained[selected]=False;normal=np.zeros_like(W)
 for k in range(3):np.add.at(normal,WF[retained,k],facecross[retained])
 normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-15);center=ap.mean(0);supports=[];support_z=[];skipped=[]
 for k,(q,n)in enumerate(zip(outer,normal[boundary_ids])):
  direction=center-q[:2];direction/=np.linalg.norm(direction);xy=q[:2]+direction*.0008
  if n[2]<.25 or not inside(xy[None,:],outer[:,:2])[0]or inside(xy[None,:],ap)[0]:skipped.append(k);continue
  dz=-float(n[:2]@(xy-q[:2]))/n[2]
  if abs(dz)>.0015:skipped.append(k);continue
  supports.append(xy);support_z.append(q[2]+dz)
 supports=np.array(supports).reshape(-1,2);num_o=len(outer);num_a=len(ap);V0=np.vstack([outer[:,:2],ap,supports]);segments=np.vstack([np.c_[np.arange(num_o),np.roll(np.arange(num_o),-1)],np.c_[num_o+np.arange(num_a),num_o+np.roll(np.arange(num_a),-1)]]);result=triangle.triangulate({'vertices':V0,'segments':segments},'pq25a0.0000002Y');V=result['vertices'];T=result['triangles'];assert np.allclose(V[:len(V0)],V0,atol=1e-12,rtol=0);cross=(V[T[:,1],0]-V[T[:,0],0])*(V[T[:,2],1]-V[T[:,0],1])-(V[T[:,1],1]-V[T[:,0],1])*(V[T[:,2],0]-V[T[:,0],0]);assert(cross>1e-14).all();is_cap=inside(V[T].mean(1),ap);skinT=T[~is_cap];capT=T[is_cap];annulus_area=float(cross[~is_cap].sum()/2);expected_area=signed_area(outer[:,:2])-signed_area(ap);assert abs(annulus_area-expected_area)<1e-12;all_outer=np.arange(num_o);support_ids=np.arange(num_o+num_a,len(V0));known=np.r_[all_outer,support_ids];values=np.r_[outer[:,2],support_z];baseline=harmonic(V,T,known,values)
 cov=np.cov((ap-center).T);_,basis=np.linalg.eigh(cov);u=basis[:,-1]
 if u[0]<0:u=-u
 v=np.array([-u[1],u[0]]);B=np.stack([u,v],axis=1);local=(V-center)@B;rim=(ap-center)@B;axis=np.max(abs(rim),axis=0)*[1.30,1.90]+.001;radius2=np.sum((local/axis)**2,axis=1);rimids=num_o+np.arange(num_a);h=np.sqrt(np.maximum(1-radius2,1e-12));depth=.008;design=np.c_[np.ones(num_a),rim];coef=np.linalg.lstsq(design,baseline[rimids]-depth*h[rimids],rcond=None)[0];rimZ=design@coef+depth*h[rimids];residual=abs(rimZ-baseline[rimids]);fit_diagnostic={'eye':name,'rim_residual_max_m':float(residual.max()),'rim_residual_mean_m':float(residual.mean()),'baseline_rim_min_max_m':[float(baseline[rimids].min()),float(baseline[rimids].max())],'fit_rim_min_max_m':[float(rimZ.min()),float(rimZ.max())],'worst_aperture_index':int(np.argmax(residual)),'depth_plane':coef.tolist(),'outer_z':outer[:,2].tolist(),'support_z':support_z};(r/'checks'/f'white_eye06_{name}_fit_diagnostic.json').write_text(json.dumps(fit_diagnostic,indent=2));np.savez_compressed(r/'checks'/f'white_eye06_{name}_fit_diagnostic.npz',vertices_xy=V,triangles=T,baseline_z=baseline,aperture_xy=ap,baseline_rim_z=baseline[rimids],fit_rim_z=rimZ,outer_positions=outer);print(fit_diagnostic,flush=True)
 report[name]=fit_diagnostic
d.close();print({name:{k:v for k,v in q.items()if k not in ["outer_z","support_z"]}for name,q in report.items()},flush=True)
