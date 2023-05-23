import json
import xlsxwriter
from pylab import array
import random
from tqdm import tqdm
import math

# --------------PARAMETERS--------------


global contamination_chance
global death_chance
global nb_basics
global nb_contaminated
global nb_shop
global duration_contamination
global duration_immunity
global iterations
global sub_iterations

contamination_chance = 0.05
death_chance = 0.01
nb_basics = 2000
nb_contaminated = 10
nb_shop = 20
duration_contamination = 2
duration_immunity = 6
iterations = 200
sub_iterations = 6
sheet_name = 'result'

# --------------OTHER VARIABLES--------------

nb_blob = nb_contaminated + nb_basics

global data
data = []

global cell_format
global header_format
global header2_format
global nb_immune
nb_immune = 0

global workbook
global worksheet
workbook = xlsxwriter.Workbook(sheet_name+'.xlsx')
worksheet = workbook.add_worksheet()


# --------------DEF--------------


def configuration():

    for i in range(nb_contaminated):
        result = {
            'status': 'contaminated',
            'living': 1,
            'immunization_time': 0,
            'contamination_time': 0
        }
        data.append(result)

    for i in range(nb_contaminated, nb_contaminated + nb_basics):
        result = {
            'status': 'basic',
            'living': 1,
            'immunization_time': 0,
            'contamination_time': 0
        }
        data.append(result)

# --------------


def choose():

    for i in (data):

        if i['living'] == 1:
            for u in range(3):
                if (random.random() > 0.5):
                    choice = random.randint(1, nb_shop)
                    time = random.randint(1, sub_iterations)
                    i['choice'+str(u)] = choice
                    i['time'+str(u)] = time
                else:
                    i['choice'+str(u)] = 0

# --------------



def potential_contamination(id_contaminated):
    if (random.random() < contamination_chance):
        id_contaminated['status'] = 'contaminated'

# --------------

def contamination_check():

    for i in (data):

        if (i['status'] == 'contaminated') and (i['living'] == 1):

            for u in (data):

                if (u['living'] == 1) and (i != u) and (u['status'] == 'basic'):

                    for y in range(3):
                        if (i['choice'+str(y)] == u['choice'+str(y)]) and (i['choice'+str(y)] + u['choice'+str(y)] > 1):
                            if (i['time'+str(y)] == u['time'+str(y)]):
                                potential_contamination(u)

            if (random.random() < round((death_chance/duration_contamination), 5)):
                i['living'] = 0

# --------------

def writing_initialization():

    global cell_format
    global header_format
    global header2_format

    cell_format = workbook.add_format()
    cell_format.set_align('center')
    cell_format.set_align('vcenter')
    cell_format.set_font_name('Avenir Next')

    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_align('vcenter')
    header_format.set_font_name('Avenir Next')
    header_format.set_bold()
    header_format.set_bg_color('#BEBEBE')

    header2_format = workbook.add_format()
    header2_format.set_align('center')
    header2_format.set_align('vcenter')
    header2_format.set_font_name('Avenir Next')
    header2_format.set_bold()
    header2_format.set_bg_color('#DCDCDC')

    worksheet.write('A1', 'Time', header_format)
    worksheet.write('B1', 'Contaminated', header_format)
    worksheet.write('C1', 'Immune', header_format)
    worksheet.write('D1', 'Basics', header_format)
    worksheet.write('A2', 0, header2_format)
    worksheet.write('B2', nb_contaminated, cell_format)
    worksheet.write('C2', nb_immune, cell_format)
    worksheet.write('D2', nb_basics, cell_format)

# --------------

def write(i):
    worksheet.write('A'+str(i+3), i+1, header2_format)
    worksheet.write('B'+str(i+3), nb_contaminated, cell_format)
    worksheet.write('C'+str(i+3), nb_immune, cell_format)
    worksheet.write('D'+str(i+3), nb_basics, cell_format)

# --------------

def counters():

    for i in (data):

        if (i['status'] == 'contaminated') and (i['living'] == 1):

            if (i['contamination_time'] <= duration_contamination):
                i['contamination_time'] += 1/sub_iterations
            if (i['contamination_time'] > duration_contamination):
                i['status'] = 'immune'
                i['contamination_time'] = 0
            
        if (i['status'] == 'immune'):

            if (i['immunization_time'] <= duration_immunity):
                i['immunization_time'] += 1/sub_iterations
            if (i['immunization_time'] > duration_immunity):
                i['status'] = 'basic'
                i['immunization_time'] = 0

def count():

    global nb_contaminated
    global nb_basics
    global nb_immune
    
    nb_contaminated = 0
    nb_basics = 0
    nb_immune = 0

    for i in (data):
        if (i['living'] == 1):
            if (i['status'] == 'contaminated'):
                nb_contaminated += 1
            if (i['status'] == 'immune'):
                nb_immune += 1
            if (i['status'] == 'basic'):
                nb_basics += 1

# --------------ITERATIONS--------------

configuration()
writing_initialization()

for i in tqdm(range(iterations)):
    choose()

    for u in range(sub_iterations):

        contamination_check()

        counters()

        count()

        write(i*sub_iterations+u)

# --------------CHART--------------

chart = workbook.add_chart({'type': 'area', 'subtype': 'stacked'})

chart.add_series(
    {
        'name': 'Contaminated',
        'categories': '=Sheet1!$A$2:$A$'+str(iterations+2),
        'values': '=Sheet1!$B$2:$B$'+str(iterations+2),
        'fill': {'color': '#ffcccb'}
    }
)

chart.add_series(
    {
        'name': 'Immune',
        'categories': '=Sheet1!$A$2:$A$'+str(iterations+2),
        'values': '=Sheet1!$C$2:$C$'+str(iterations+2),
        'fill': {'color': '#808080'}
    }
)

chart.add_series(
    {
        'name': 'Basics',
        'categories': '=Sheet1!$A$2:$A$'+str(iterations+2),
        'values': '=Sheet1!$D$2:$D$'+str(iterations+2),
        'fill': {'color': '#90EE90'}
    }
)

chart.set_y_axis({
    'max': nb_blob*1.2
})

worksheet.insert_chart("F1", chart)

# --------------END--------------

workbook.close()

with open("data.json", "w") as outfile:
    json.dump(data, outfile)