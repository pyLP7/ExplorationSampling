import os
import time


class CS_log():
    '''
    Through the CS_log python class, the CS_log_file will be written
    Actions taken by CS-OPT will be described step-by-step
    '''

    def __init__(
            self,
            path_to_save,
            filename='cs_opt.log',
            format_time=8,
            format_date=10,
            filemode='w'):

        self.filename = filename
        self.format_time = format_time
        self.format_date = format_date
        self.filemode = filemode
        self.month = [
            'Jan',
            'Feb',
            'Mar',
            'Apr',
            'May',
            'Jun',
            'Jul',
            'Aug',
            'Sep',
            'Oct',
            'Nov',
            'Dec']
        self.actual_path = path_to_save #os.getcwd()

    def file_write(self, output_str, flag=2):
        output_str += '\n'
        if os.path.isfile(
            self.actual_path +
            '/' +
                self.filename) and flag == 2:
            F = open(self.actual_path + '/' + self.filename, 'a')
        # elif  flag == 1:
        else:
            F = open(self.actual_path + '/' + self.filename, 'w')
        for i in range(len(output_str)):
            F.write(str(output_str[i]))
        F.close()

    def get_time(self):
        timer = time.localtime()

        if timer[2] < 10:
            day = '0' + str(timer[2])
        else:
            day = str(timer[2])

        if timer[3] < 10:
            hour = '0' + str(timer[3])
        else:
            hour = str(timer[3])

        if timer[4] < 10:
            minitutes = '0' + str(timer[4])
        else:
            minitutes = str(timer[4])

        if timer[5] < 10:
            secs = '0' + str(timer[5])
        else:
            secs = str(timer[5])

        date = str(timer[3]) + '-' + str(self.month[timer[1] - 1]) + '-' + day
        clock = hour + ':' + minitutes + ':' + secs + ' '
        output_inf = [date, clock]
        return output_inf

    def header(self):
        ''' Integrates the CS - Log Header'''

        output_str = [
            '\n',
            '\n',
            '   **************     **************                *                  **************      **************  \n',
            '   *                  *                             *                  *            *      *               \n',
            '   *                  *                             *                  *            *      *               \n',
            '   *                  *                             *                  *            *      *               \n',
            '   *                  *                             *                  *            *      *               \n',
            '   *                  **************    *******     *                  *            *      *   **********  \n',
            '   *                               *                *                  *            *      *            *  \n',
            '   *                               *                *                  *            *      *            *  \n',
            '   *                               *                *                  *            *      *            *  \n',
            '   *                               *                *                  *            *      *            *  \n',
            '   *                               *                *                  *            *      *            *  \n',
            '   **************     **************                **************     **************      **************',
            '\n',
            '\n']
        CS_log.file_write(self, output_str, 1)

    def info(self, string):

        date = CS_log.get_time(self)
        output_str = [
            date[0] +
            ' | ' +
            date[1] +
            '| - INFO - | ' +
            string +
            '\n']
        CS_log.file_write(self, output_str, 2)

    def error(self, string):

        date = CS_log.get_time(self)
        output_str = [
            date[0] +
            ' | ' +
            date[1] +
            '| - ERROR- | ' +
            string +
            '\n']
        CS_log.file_write(self, output_str, 2)

    def warn(self, string):

        date = CS_log.get_time(self)
        output_str = [
            date[0] +
            ' | ' +
            date[1] +
            '| - WARN - | ' +
            string +
            '\n']
        CS_log.file_write(self, output_str, 2)

    def main(self, string):

        date = CS_log.get_time(self)
        line_1 = '************************************************************************************************************\n'
        line_2 = date[0] + ' | ' + date[1] + '| - MAIN - | ' + string + '\n'
        output_str = ['\n', line_1, line_2, line_1, '\n']
        CS_log.file_write(self, output_str, 2)


def out_print(self, string):

    if self.log_file:
        self.clog.file_write(string)
    # print in the console anyway
    print(string)
