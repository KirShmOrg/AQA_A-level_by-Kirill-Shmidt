from class_database import db
from component_classes.class_cpu import CPU
from component_classes.class_gpu import GPU
# from component_classes.class_motherboard import Motherboard

db.update_filters('CPU', 'GPU', 'MB')
cpu_list = db.get_cpu_list(params={"mfgr": 'AMD',
                                   "released": '2022',
                                   "mobile": 'No',
                                   "server": 'No',
                                   "multiUnlocked": 'Yes'})
print(len(cpu_list), cpu_list)
for i_cpu in cpu_list:
    i_cpu = CPU(i_cpu)
    if i_cpu.exists:
        print(i_cpu)
    else:
        del i_cpu

# gpu_list = db.get_gpu_list(params={'mfgr': 'NVIDIA',
#                                    'released': '2023',
#                                    'mobile': 'No',
#                                    'workstation': 'No',
#                                    'performance': '1080'})
# print(len(gpu_list), gpu_list)
# for i_gpu in gpu_list:
#     i_gpu = GPU(i_gpu)
#     print(i_gpu)
#
# mb_list = db.get_mb_list(params={'manufacturer': 'Asus',
#                                  'form_factor': 'Micro-ATX',
#                                  'socket': 'AM4',
#                                  'chipset': 'AMD B450',
#                                  })
# print(len(mb_list), mb_list)