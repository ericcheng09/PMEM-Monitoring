import subprocess
import re, json


class PMEM():
    def __init__(self):
        self.health_stats_mapping = {
            "Healthy": 0,
            "Noncritical": 1,
            "Critical": 2,
            "Fatal": 3,
            "Non-Functional": 4,
            "Unmanageable": 5,
            "Unknown": 6
        }

    # def _get_all_pmem(self): # discover devices
    #     output = str(subprocess.check_output("ipmctl show -a -u B -dimm", shell=True))
    #     keys = re.findall("[a-zA-Z]+=", output)
    #     keys = [key[:len(key) - 1] for key in keys]
    #     # values = re.findall("=[a-zA-Z0-9]+", output)
    #     values = re.findall("=.+\n", output)
    #     values = [value[1:len(value) - 1] for value in values]
    #     for idx, key in enumerate(keys):
    #         if key == "DimmID":
    #             id = values[idx].replace("-","")
    #             self.devices.append(id)
    #             self.device_info[id] = {}
    #             continue
    #         self.device_info[self.devices[-1]][key] = values[idx]

    def _get_usage(self):
        output_ndctl = json.loads(str(subprocess.check_output("ndctl list -N", shell=True, encoding='UTF-8')))
        size = 0.0
        for namespace in output_ndctl:
            size += namespace["size"]

        # output_ipmctl = str(subprocess.check_output("ipmctl show -u B -d Capacity -dimm", shell=True, encoding='UTF-8'))
        # keys = re.findall("[a-zA-Z]+=", output_ipmctl)
        # keys = [key[:len(key) - 1] for key in keys]
        # values = re.findall("=[a-zA-Z0-9]+", output_ipmctl)
        # values = [value[1:] for value in values]
        # tmp_dimm = None
        # for idx, key in enumerate(keys):
        #     if key == "Capacity":
        #         total_size += float(values[idx])

        return size, output_ndctl

    def _get_sensor_info(self):
        sensor_info = {}
        output = str(subprocess.check_output("ipmctl show -a -sensor -dimm", shell=True, encoding='UTF-8'))
        keys = re.findall("[a-zA-Z]+=", output)
        keys = [key[:- 1] for key in keys]
        # values = re.findall("=[a-zA-Z0-9]+", output)
        values = re.findall("=.+\n", output)
        values = [value[1:- 1] for value in values]

        tmp_id, tmp_type = None, None
        for idx, key in enumerate(keys):
            if key == "DimmID":
                dimmid = values[idx].replace("-", "")
                tmp_id = dimmid
                sensor_info[dimmid] = {}
                continue
            elif key == "Type":
                tmp_type = values[idx]
                sensor_info[tmp_id][tmp_type] = {}
                continue
            sensor_info[tmp_id][tmp_type][key] = values[idx]
        return sensor_info


    def get_data(self):
        data = []
        total_size = 0.0
        try:
            output = str(subprocess.check_output("ipmctl show -performance MediaReads,MediaWrites", shell=True, encoding='UTF-8'))
            data_dict = {}
            keys = re.findall("[a-zA-Z]+=", output)
            keys = [key[:-1] for key in keys]
            values = re.findall("=[a-zA-Z0-9]+", output)
            values = [value[1:] for value in values]

            sensor_info = self._get_sensor_info()
            for idx, key in enumerate(keys):
                tmp = data_dict.get(key, [])
                tmp.append(values[idx])
                data_dict[key] = tmp

            for idx, Dimm in enumerate(data_dict["DimmID"]):
                data.append(
                    'PMEM' + ',DIMM=' + Dimm + ',Type=Physical' + \
                     ' MediaReads={}'.format(int(data_dict["MediaReads"][idx], 0) * 64) + \
                    ',MediaWrites={}'.format(int(data_dict["MediaWrites"][idx], 0) * 64) + \
                    ',Health={}'.format(self.health_stats_mapping[sensor_info[Dimm]["Health"]["CurrentValue"]]) + \
                    ',LifePercentageRemaining={}'.format(sensor_info[Dimm]["PercentageRemaining"]["CurrentValue"][:-1]) + \
                    ',UpTime={}'.format(sensor_info[Dimm]["UpTime"]["CurrentValue"][:-1]) + \
                    ',MediaTemperature={}'.format(sensor_info[Dimm]["MediaTemperature"]["CurrentValue"][:-1]) + \
                    ',ControllerTemperature={}'.format(sensor_info[Dimm]["ControllerTemperature"]["CurrentValue"][:-1])
                )

            output_ipmctl = str(subprocess.check_output("ipmctl show -u B -d Capacity -dimm", shell=True, encoding='UTF-8'))
            keys = re.findall("[a-zA-Z]+=", output_ipmctl)
            keys = [key[:len(key) - 1] for key in keys]
            values = re.findall("=[a-zA-Z0-9]+", output_ipmctl)
            values = [value[1:] for value in values]
            for idx, key in enumerate(keys):
                if key == "Capacity":
                    total_size += float(values[idx])

        except Exception as e:
            print(e)

        try:
            usage = self._get_usage()
            data.append(
               'PMEM,Total={}'.format(int(total_size) / 1024 / 1024 / 1024) + ',Type=Virtual' +\
                ' UsableCapacityPercentage={}'.format((1 - usage[0]/total_size) * 100)
            )

            for namespace in usage[1]:
                data.append(
                    'Namespace,BlockDevice=' + namespace["blockdev"] + ' size={}'.format(namespace["size"])
                )
        except Exception as e:

            data.append(
                'PMEM,Total={}'.format(int(total_size) / 1024 / 1024 / 1024) + ',Type=Virtual' + \
                ' UsableCapacityPercentage={}'.format(100.0)
            )
            pass

        for d in data:
            print(d)

if __name__ == "__main__":
    pmem = PMEM()
    pmem.get_data()
