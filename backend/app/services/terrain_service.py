from pathlib import Path
import math
import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.mask import mask
from rasterio.merge import merge
from shapely.geometry import box, mapping

BASE_DIR=Path(__file__).resolve().parents[3]
SRTM_DIRECTORY=BASE_DIR/'datasets'/'srtm'/'raw_tiles'
AOI_OFFSET=0.05
def _create_aoi(lat,lon): return box(lon-AOI_OFFSET,lat-AOI_OFFSET,lon+AOI_OFFSET,lat+AOI_OFFSET)
def _find_tiles(aoi):
    ts=[]
    for t in sorted(SRTM_DIRECTORY.glob('*.tif')):
        with rasterio.open(t) as ds:
            if box(*ds.bounds).intersects(aoi): ts.append(t)
    if not ts: raise FileNotFoundError('No SRTM tiles intersect the AOI.')
    return ts
def _merge(ts):
    d=[rasterio.open(x) for x in ts]
    try:
        m,tr=merge(d); meta=d[0].meta.copy(); meta.update(height=m.shape[1],width=m.shape[2],transform=tr,count=1,driver='GTiff'); return m,meta
    finally:
        [x.close() for x in d]
def _clip(m,meta,aoi):
    with MemoryFile() as mem:
        with mem.open(**meta) as ds:
            ds.write(m)
            c,tr=mask(ds,[mapping(aoi)],crop=True,filled=False)
            return np.ma.masked_invalid(c[0]),tr
def get_terrain_features(latitude:float,longitude:float):
    aoi=_create_aoi(latitude,longitude)
    m,meta=_merge(_find_tiles(aoi))
    elev,tr=_clip(m,meta,aoi)
    if elev.count()==0: raise ValueError('No valid elevation cells.')
    pw=abs(tr.a)*(111320*math.cos(math.radians(latitude))); ph=abs(tr.e)*110574
    arr = elev.astype(np.float64).filled(np.nan)
    gy,gx=np.gradient(arr,ph,pw)
    slope=np.ma.masked_invalid(np.degrees(np.arctan(np.sqrt(gx**2+gy**2))))
    ms=float(np.mean(slope.compressed()))
    terr='FLAT' if ms<3 else 'GENTLE' if ms<8 else 'MODERATE' if ms<15 else 'STEEP'
    return {'success':True,'elevation':float(np.mean(elev.compressed())),'slope':ms,'terrain':terr}