import _DOE_class

if __name__ == "__main__":
    
    doe_type = 'Sobol'
    
    random_seed = 42
    
    dd = 2
    nn = 20
    
    gen_doe_sobol = _DOE_class.DOE_Class('sobol', repeat=random_seed).DOE
    gen_doe_MIPT = _DOE_class.DOE_Class('MIPT', repeat=random_seed, sizeOneStage=10).DOE
    gen_doe_MqPLHS = _DOE_class.DOE_Class('MqPLHS', repeat=random_seed, sizeOneStage=10).DOE
    gen_doe_FpPLHS = _DOE_class.DOE_Class('FpPLHS', repeat=random_seed, sizeOneStage=10).DOE

    
    # print(gen_doe_sobol(dd,nn))
    print(gen_doe_MIPT(dd,nn))
    # print(gen_doe_MqPLHS(dd,nn))
    # print(gen_doe_FpPLHS(dd,nn))
    