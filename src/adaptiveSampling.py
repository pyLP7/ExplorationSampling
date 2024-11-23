from utils import DOE_class

if __name__ == "__main__":
    
    # define the dimension (dd, i.e. number of variables) and size (nn, max number of samples) of your DoE
    dd = 2
    nn = 16
    
    # repeatability
    random_seed = 42
    
    # generate the 
    # gen_doe_sobol = DOE_class.DOE_Class('sobol', repeat=random_seed).DOE
    gen_doe_MIPT = DOE_class.DOE_Class('MIPT', repeat=random_seed, sizeOneStage=10).DOE
    # gen_doe_MqPLHS = DOE_class.DOE_Class('MqPLHS', repeat=random_seed, sizeOneStage=10).DOE
    # gen_doe_FpPLHS = DOE_class.DOE_Class('FpPLHS', repeat=random_seed, sizeOneStage=10).DOE

    # 
    X = gen_doe_MIPT(dd,nn)
    # print(gen_doe_sobol(dd,nn))
    print(gen_doe_MIPT(dd,nn))
    # print(gen_doe_MqPLHS(dd,nn))
    # print(gen_doe_FpPLHS(dd,nn))
    