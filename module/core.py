import OpenEXR, Imath
import numpy as np
import copy

def is_ok(path):
    if not OpenEXR.isOpenExrFile(path): 
        return False
    img = OpenEXR.InputFile(path)
    if not img.isComplete():
        return False
    return True
    
def load(path):
    exr = OpenExr(path)
    exr.load()
    return exr.channels()

def save(path, img):
    exr = OpenExr(path)
    exr.channels = img
    exr.save()

class OpenExr:
    def __init__(self, path = ""):
        print(1)
        self._channels = dict()
        self._path = str(path)
        self._shape = None
        
        self._rewrite = False # rewrite exist file when is exist
        self._preserve_channels = True # Do not delete existing channels if the new channels are loaded from file 
        print(2)
    
    def load(self, path = ""):
        if type(path) is not str:
            raise TypeError("Path must be string")
        if path == "":
            path = self._path
        if path == "":
            raise ValueError("Path must be set")
        if not OpenEXR.isOpenExrFile(path): 
            raise FileNotFoundError(path)
        img = OpenEXR.InputFile(path)
        if not img.isComplete():
            raise IOError("File is corrupted")
        dw = img.header()['displayWindow']
        size = (dw.max.y - dw.min.y + 1, dw.max.x - dw.min.x + 1)
        
        if self._shape is None:
            self._shape = size
        elif self._shape != size:
            raise ValueError("Shapes must be same - " + str(self._shape) + " vs " + str(size) ) 
        
        for channel_name, channel_type in img.header()["channels"].items():
            # data
            data = img.channel(channel_name)
            
            # pixel data type
            pix_type = np.float32
            if channel_type == Imath.Channel( Imath.PixelType( Imath.PixelType.HALF ) ):
                pix_type = np.float16
            elif channel_type == Imath.Channel( Imath.PixelType( Imath.PixelType.UINT ) ):
                pix_type = np.np.uint64
                
            # create numpy channel in dictionary
            if channel_name not in self or self._preserve_channels:
                self[channel_name] = np.fromstring(data, dtype = pix_type).reshape(size)
        
    def save(self, path = ""):
        if type(path) is not str:
            raise TypeError("Path must be string")
        if path == "":
            path = self._path
        if path == "":
            raise ValueError("Path must be set")
        if self._shape is None:
            raise ValueError("No data")
        channels_data = dict()
        channels_type = dict()
        height, width = self._shape
        for _key, _channel in self.items():
            # data
            pixels = _channel.tostring()
            
            # pixel data type
            pix_type = Imath.Channel( Imath.PixelType( Imath.PixelType.FLOAT ) )
            if _channel.dtype == np.float16:
                pix_type = Imath.Channel( Imath.PixelType( Imath.PixelType.HALF ) )
            elif _channel.dtype in (np.uint, np.uint8, np.uint16, np.uint32, np.uint64):
                pix_type = Imath.Channel( Imath.PixelType( Imath.PixelType.UINT ) )
            # other types is represented as float
            
            # assign
            channels_data[_key] = pixels
            channels_type[_key] = pix_type
        
        # prepare exr header
        HEADER = OpenEXR.Header(width, height)
        HEADER["channels"] = channels_type
        
        # write data and save to file
        exr = OpenEXR.OutputFile(path, HEADER)
        exr.writePixels(channels_data)
        exr.close()
    
    def __iadd__(self, obj):
        if type(obj) is OpenExr:
            for key, value in obj.items():
                if key in self:
                    self[key] += value
                    continue
                self[key] = value
            return self
        if isinstance(obj, (int, float)) or np.issubdtype(obj, np.number):
            for key in self.keys():
                self[key] += obj
            return self
        raise TypeError("Object must be type of int, float or OpenExr, not " + str( type( obj) ) )
    
    def __isub__(self, obj):
        if type(obj) is OpenExr:
            for key, value in obj.items():
                if key in self:
                    self[key] -= value
                    continue
                self[key] = value*(-1)
            return self
        if isinstance(obj, (int, float)) or np.issubdtype(obj, np.number):
            for key in self.keys():
                self[key] -= obj
            return self
        raise TypeError("Object must be type of int, float or OpenExr, not " + str( type( obj) ) )
        
    def __imul__(self, obj):
        if type(obj) is OpenExr:
            for key, value in obj.items():
                if key in self:
                    self[key] *= value
            return self
        if isinstance(obj, (int, float)) or np.issubdtype(obj, np.number):
            for key in self.keys():
                self[key] *= obj
            return self
        raise TypeError("Object must be type of int, float or OpenExr, not " + str( type( obj) ) )
        
    def __itruediv__(self, obj):
        if type(obj) is OpenExr:
            for key, value in obj.items():
                if key in self:
                    self[key] /= value
            return self
        if isinstance(obj, (int, float)) or np.issubdtype(obj, np.number):
            for key in self.keys():
                self[key] /= obj
            return self
        raise TypeError("Object must be type of int, float or OpenExr, not " + str( type( obj) ) )
    
    def __ifloordiv__(self, obj):
        if type(obj) is OpenExr:
            for key, value in obj.items():
                if key in self:
                    self[key] //= value
            return self
        if isinstance(obj, (int, float)) or np.issubdtype(obj, np.number):
            for key in self.keys():
                self[key] //= obj
            return self
        raise TypeError("Object must be type of int, float or OpenExr, not " + str( type( obj) ) )
        
    def __imod__(self, obj):
        if type(obj) is OpenExr:
            for key, value in obj.items():
                if key in self:
                    self[key] %= value
            return self
        if isinstance(obj, (int, float)) or np.issubdtype(obj, np.number):
            for key in self.keys():
                self[key] %= obj
            return self
        raise TypeError("Object must be type of int, float or OpenExr, not " + str( type( obj) ) )
    
    def __ipow__(self, obj):
        if type(obj) is OpenExr:
            for key, value in obj.items():
                if key in self:
                    self[key] **= value
            return self
        if isinstance(obj, (int, float) ) or np.issubdtype(obj, np.number):
            for key in self.keys():
                self[key] **= obj
            return self
        raise TypeError("Object must be type of int, float, numpy number or OpenExr, not " + str( type( obj) ) )
    
    def __add__(self, obj):
        clone = self.copy()
        clone += obj
        return clone
    
    def __sub__(self, obj):
        clone = self.copy()
        clone -= obj
        return clone
        
    def __mul__(self, obj):
        clone = self.copy()
        clone *= obj
        return clone
        
    def __truediv__(self, obj):
        clone = self.copy()
        clone /= obj
        return clone
    
    def __floordiv__(self, obj):
        clone = self.copy()
        clone //= obj
        return clone
        
    def __mod__(self, obj):
        clone = self.copy()
        clone %= obj
        return clone
    
    def __pow__(self, obj):
        clone = self.copy()
        clone **= obj
        return clone
    
    def merge(self, obj):
        if type(obj) is not OpenExr:
            raise TypeError("Parameter must be OpenExr object")
        if self._shape is None:
            self._shape = obj._shape
        for key, value in obj.items():
            if key not in self or self._preserve_channels:
                self[key] = value
        return self
        
    def max(self, channel = None):
        if channel is not None:
            return np.max( self[channel] )
        v = None
        for ch in self.values():
            _max = np.max(ch)
            if v is None:
                v = _max
                continue
            if _max > v:
                v = _max
        return v 
        
    def min(self, channel = None):
        if channel is not None:
            return np.max( self[channel] )
        v = None
        for ch in self.values():
            _min = np.min(ch)
            if v is None:
                v = _min
                continue
            if _min > v:
                v = _min
        return v
        
    def sum(self, channel = None):
        if channel is not None:
            return np.sum( self[channel] )
        v = 0
        for ch in self.values():
            v += np.sum(ch)
        return v
    
    # element wise
    def max_element_wise(self):
        mat = None
        for ch in self.values():
            if mat is None:
                mat = ch
                continue
            mat = np.maximum( mat, ch )
        return mat
    
    # element wise
    def min_element_wise(self):
        mat = None
        for ch in self.values():
            if mat is None:
                mat = ch
                continue
            mat = np.minimum( mat, ch )
        return mat
    
    # element wise
    def sum_element_wise(self):
        mat = None
        for ch in self.values():
            if mat is None:
                mat = ch
                continue
            mat += ch
        return mat
    
    @property
    def shape(self):
        return self._shape
    
    def channel(self, name):
        return self._channels[ str(name) ]
        
    @property
    def channels(self):
        return self._channels
    
    @channels.setter
    def channels(self, channels):
        if type(channels) is not dict:
            raise TypeError("Parametr must be dictionary type")
        self.clear()
        self.add_channels(channels)
    
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, path):
        if type(path) is not str:
            raise TypeError("Path must be string")
        self._path = path
    
    @property
    def option_preserve_channels(self):
        return self._preserve_channels
    
    @option_preserve_channels.setter
    def option_preserve_channels(self, preserve_channels):
        if type(path) is not bool:
            raise TypeError("Parameter must be bool")
        self._preserve_channels = preserve_channels
    
    @property
    def option_rewrite_files(self):
        return self._rewrite
    
    @option_rewrite_files.setter
    def option_rewrite_files(self, rewrite):
        if type(rewrite) is not bool:
            raise TypeError("Parameter must be bool")
        self._rewrite = rewrite
    
    def add_channels(self, channels):
        for key, item in channels.items:
            self[key] = item
            
    def __setitem__(self, key, item):
        if type(key) is not str:
            raise TypeError("Type of key must be string")
        if type(item) is not np.ndarray:
            raise TypeError("Type of item must be numpy array, not " + str(type(item) ) )
        if len(item.shape) != 2:
            raise ValueError("Numpy matrix must be 2D")
        if self._shape is None:
            self._shape = item.shape
        elif self._shape != item.shape:
            raise ValueError("Shapes must be same - " + str(self._shape) + " vs " + str(size) ) 
        self._channels[key] = item

    def __getitem__(self, key):
        return self._channels[str(key)]

    def __repr__(self):
        path = self._path
        if path != "":
            path = "(" + path + ")"
        saved = "[Saved] " if self._saved else "[Unsaved] "
        return saved + "OpenExr object " + path + " which contain " + str(len(self._channels) ) + " layers"
    
    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self._channels)

    def __delitem__(self, key):
        del self._channels[key]

    def clear(self):
        return self._channels.clear()

    def has_key(self, k):
        return k in self._channels

    def update(self, *args, **kwargs):
        channels = dict()
        channels.update(*args, **kwargs)
        OpenExr._check_dict_consistency(channels)
        return self._channels.update(**channels)

    def keys(self):
        return self._channels.keys()

    def values(self):
        return self._channels.values()

    def items(self):
        return self._channels.items()

    def pop(self, *args):
        return self._channels.pop(*args)

    def __contains__(self, item):
        return item in self._channels

    def __iter__(self):
        return iter(self._channels)
                
    def copy(self, deep = True):
        if deep:
            return copy.deepcopy(self)
        return copy.copy(self)
        
    
    
