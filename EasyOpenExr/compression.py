
import OpenEXR, Imath

def str_to_obj(string):
    return {
        "no_compression" : NoCompression(), 
        "rle_compression" : Rle(),
        "zips_compression" : Zips(),
        "zip_compression" : Zip(),
        "piz_compression" : Piz(),
        "pxr24_compression" : Pxr24(),
        "nocompression" : NoCompression(), 
        "rle" : Rle(),
        "zips" : Zips(),
        "zip" : Zip(),
        "piz" : Piz(),
        "pxr24" : Pxr24(),
    }[str(string).lower()]

class __Compression:
    def __init__(self):
        self._compression = Imath.Compression.ZIP_COMPRESSION
    
    @property
    def compression(self):
        return Imath.Compression(self._compression)
    
    def __str__(self):
        return str(self.compression)

    def __repr__(self):
        return str(self)

class NoCompression(__Compression):
    def __init__(self):
        self._compression = Imath.Compression.NO_COMPRESSION

class Rle(__Compression):
    def __init__(self):
        self._compression = Imath.Compression.RLE_COMPRESSION

class Zips(__Compression):
    def __init__(self):
        self._compression = Imath.Compression.ZIPS_COMPRESSION

class Zip(__Compression):
    def __init__(self):
        self._compression = Imath.Compression.ZIP_COMPRESSION
        self._compression

class Piz(__Compression):
    def __init__(self):
        self._compression = Imath.Compression.PIZ_COMPRESSION

class Pxr24(__Compression):
    def __init__(self):
        self._compression = Imath.Compression.PXR24_COMPRESSION
