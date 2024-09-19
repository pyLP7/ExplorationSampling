import os
from subprocess import check_output,run
import concurrent.futures
import multiprocessing as mp

class parallel_processing():
    '''
    ### write documentation PARALLEL Processing
    '''
    def __init__(self):
        pass
            
    def run_parallel_jobs(self, ith_job):
        
        # time.sleep(70)
        command = str(ith_job[0])
        surrounding = str(ith_job[1])
        os.chdir(surrounding)
        # run
        check_output(command,shell=False)
        
        return '### '+ith_job[1].split('\\')[-1]+' done ###'
    
    def set_parallel_jobs(self, process_list, n_par_jobs, n_par_opti=None):
        # if not DOE
        if n_par_opti:
            # if no parallel jobs allowed
            if n_par_opti == 1:
                print(self.run_parallel_jobs(process_list[0]))
                return
            # if the # of new points per iteratio <= parallel jobs
            elif n_par_opti<=n_par_jobs:
                n_par_jobs=n_par_opti
            else:
                n_par_jobs=1
        
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # total number of jobs
            tot_numb_jobs = len(process_list)
            # number of calls with parallel jobs running
            n_calls = int(tot_numb_jobs/n_par_jobs)
            # set the bunches of parallel jobs
            for bunch_index in range(n_calls):
                job_bunch = [ii for ii in process_list[(bunch_index)*n_par_jobs:(bunch_index+1)*n_par_jobs]]
                
                # bunch of jobs to be executed
                ex_job_bunch = [executor.submit(self.run_parallel_jobs, job) for job in job_bunch]
                for ii in concurrent.futures.as_completed(ex_job_bunch): print(ii.result())
            
            # remaining jobs (if any)
            if tot_numb_jobs % n_par_jobs!=0:
                print('### RESIDUAL JOBS ###')
                ex_job_bunch_rem= [executor.submit(self.run_parallel_jobs, job) for job in process_list[-(tot_numb_jobs-n_par_jobs*n_calls):]]
                for ii in concurrent.futures.as_completed(ex_job_bunch_rem): print(ii.result())
