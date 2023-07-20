import json
import numpy as np

class StandardScaler:
    def __init__(self,elim_zero=False):
        self.__elim_zero = elim_zero
        self.__fitdone = False
        self.__params = {'minimum':None,'maximum':None}
    
    def __check_fit(self):
        assert self.__fitdone,'ERROR: Fit/load scaler first'

    def fit(self,x):
        self.__params['minimum'] = x.min()
        self.__params['maximum'] = (x - self.__params['minimum']).max()
        self.__fitdone = True

    def transform(self,x):
        self.__check_fit()
        xt = (x - self.__params['minimum'])/self.__params['maximum']
        if self.__elim_zero:
            xttemp = xt[xt!=0]
            newmin = xttemp.min()
            xt[xt==0] = newmin
        return xt

    def fit_transform(self,x):
        self.fit(x)
        return self.transform(x)

    def reverse(self,x):
        self.__check_fit()
        return (x*self.__params['maximum']) + self.__params['minimum']
    
    def load_dict(self,params):
        assert set(list(params.keys())) == {'minimum','maximum'}
        for k,v in params.items():
            self.__params[k] = v

    def load_json(self,path):
        with open(path) as json_file:
            params = json.load(json_file)
        assert set(list(params.keys())) == {'minimum','maximum'}
        for k,v in params.items():
            self.__params[k] = v

    def save(self,path):
        self.__check_fit()
        "Save as a .json file"
        self.__check_fit()
        with open(path,'w') as json_file:
            json.dump(self.__params,json_file)
        json_file.close()

    def params(self):
        self.__check_fit()
        return self.__params