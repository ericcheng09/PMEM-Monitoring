import libvirt
from xml.etree import ElementTree

#   https://libvirt.org/
def extractInfo(conn, id):
    infos = []

    domain = conn.lookupByID(id)
    vm_name = domain.name()
    vm_uuid = domain.UUIDString()

    state, maxmem, mem, vcpus, vcputime = domain.info()
    meminfo = domain.memoryStats()
    infos.append("VM_Memory,name={},id={},uuid={} state={},actual={},available={},used={}".format(
        vm_name, id, vm_uuid,
        state, meminfo['actual'] * 1024, meminfo['available'] * 1024,
               meminfo['available'] * 1024 - meminfo['unused'] * 1024)
    )

    # print("VM_Memory,name={},id={},uuid={} state={},actual={},available={},used={}".format(
    #     vm_name, id, vm_uuid,
    #     state, meminfo['actual'] * 1024, meminfo['available'] * 1024,
    #            meminfo['available'] * 1024 - meminfo['unused'] * 1024)
    # )
    # cputime = domain.getCPUStats(True)[0]['cpu_time'] # host cpu

    for vcpu in domain.vcpus()[0]:
        vcpu_number, vcpu_state, vcpu_cputime, vcpu_realcpu = vcpu
        infos.append("VM_Vcpu,name={},id={},uuid={},vCPU={} state={},VCpuState={},VCpuTime={},CpuOnHost={}".format(
            vm_name, id, vm_uuid, vcpu_number, state, vcpu_state, vcpu_cputime, vcpu_realcpu))
        # print("VM_Vcpu,name={},id={},uuid={},vCPU={} state={},VCpuState={},VCpuTime={},CpuOnHost={}".format(
        #     vm_name, id, vm_uuid, vcpu_number, state, vcpu_state, vcpu_cputime, vcpu_realcpu))

    vm_xml = domain.XMLDesc()
    root = ElementTree.fromstring(vm_xml)

    devices = root.findall('devices/disk/target')
    for device in devices:
        read_req, read_bytes, write_req, write_bytes, error = domain.blockStats(device.get('dev'))

        infos.append("VM_BlkIO,name={},id={},uuid={},device={} state={},blkReadBytes={},blkWriteBytes={}".format(
            vm_name, id, vm_uuid, device.get('dev'),
            state, read_bytes, write_bytes))
        # print("VM_BlkIO,name={},id={},uuid={},device={} state={},blkReadBytes={},blkWriteBytes={}".format(
        #     vm_name, id, vm_uuid, device.get('dev'),
        #     state, read_bytes, write_bytes))

        capacity, allocation, physical = domain.blockInfo(device.get('dev'))
        infos.append("VM_DiskUsage,name={},id={},uuid={},device={} state={},capacity={},allocation={},physical={}".format(
            vm_name, id, vm_uuid, device.get('dev'),
            state, capacity, allocation, physical))
        # print("VM_DiskUsage,name={},id={},uuid={},device={} state={},capacity={},allocation={},physical={}".format(
        #     vm_name, id, vm_uuid, device.get('dev'),
        #     state, capacity, allocation, physical))

        # capacity : logical size in bytes of the image (how much storage the guest will see)
        # allocation : host storage in bytes occupied by the image
        # physical : host physical size in bytes of the image container
    devices = root.findall('devices/memory')
    for device in devices:
        pmem_path, pmem_size = '', 0

        memory_model = device.get('model')
        children = device.getchildren()
        for child in children:
            if child.tag == 'source':
                pmem_path = child.getchildren()[0].text

            if child.tag == 'target':
                for target_info in child.getchildren():
                    if target_info.tag == "size":
                        if target_info.get('unit') == 'KiB':
                            pmem_size = int(target_info.text) * 1024
                        else:
                            pmem_size = int(target_info.text)
        infos.append('VM_PMEM,name={},id={},uuid={},model={} state={},path="{}",size={}'.format(
            vm_name, id, vm_uuid, memory_model,
            state, pmem_path, pmem_size)
        )

        # print('VM_PMEM,name={},id={},uuid={},model={} state={},path="{}",size={}'.format(
        #     vm_name, id, vm_uuid, memory_model,
        #     state, pmem_path, pmem_size)
        # )
        # capacity : logical size in bytes of the image (how much storage the guest will see)
        # allocation : host storage in bytes occupied by the image
        # physical : host physical size in bytes of the image container
    network_interfaces = root.findall('devices/interface/target')
    for interface in network_interfaces:
        rx_bytes, rx_packets, rx_error, rx_drop, tx_bytes, tx_packets, tx_error, tx_drop = \
            domain.interfaceStats(interface.get('dev'))
        tmp = "rx_bytes={},rx_packets={},rx_error={},rx_drop={},tx_bytes={},tx_packets={},tx_error={},tx_drop={}".format(
            rx_bytes, rx_packets, rx_error, rx_drop, tx_bytes, tx_packets, tx_error, tx_drop
        )
        infos.append("VM_NetworkIO,name={},id={},uuid={},interface={} state={},".format(
            vm_name, id, vm_uuid, interface.get('dev'), state) + tmp
        )
        # print("VM_NetworkIO,name={},id={},uuid={},interface={} state={},".format(
        #     vm_name, id, vm_uuid, interface.get('dev'), state) + tmp
        #       )
        for info in infos:
            print(info)

try:
    conn = libvirt.open('qemu:///system')
    ids = conn.listDomainsID()
except Exception as e:
    ids = []
    # print(e)


for id in ids:
    try:
        extractInfo(conn, id)
    except Exception as e:
        print("id: {} failed to extract info".format(id))
        pass




# for id in ids:
#     domain = conn.lookupByID(id)
#     vm_name = domain.name()
#     vm_uuid = domain.UUIDString()
#
#     state, maxmem, mem, vcpus, vcputime = domain.info()
#     meminfo = domain.memoryStats()
#     print("VM_Memory,name={},id={},uuid={} state={},actual={},available={},used={}".format(
#         vm_name, id, vm_uuid,
#         state, meminfo['actual'] * 1024, meminfo['available'] * 1024, meminfo['available'] * 1024 - meminfo['unused'] * 1024)
#     )
#     # cputime = domain.getCPUStats(True)[0]['cpu_time'] # host cpu
#
#     for vcpu in domain.vcpus()[0]:
#         vcpu_number, vcpu_state, vcpu_cputime, vcpu_realcpu = vcpu
#         print("VM_Vcpu,name={},id={},uuid={},vCPU={} state={},VCpuState={},VCpuTime={},CpuOnHost={}".format(
#             vm_name, id, vm_uuid, vcpu_number, state, vcpu_state, vcpu_cputime, vcpu_realcpu))
#
#
#
#     vm_xml = domain.XMLDesc()
#     root = ElementTree.fromstring(vm_xml)
#
#
#     devices = root.findall('devices/disk/target')
#     for device in devices:
#         read_req, read_bytes, write_req, write_bytes, error = domain.blockStats(device.get('dev'))
#         print("VM_BlkIO,name={},id={},uuid={},device={} state={},blkReadBytes={},blkWriteBytes={}".format(
#             vm_name, id, vm_uuid, device.get('dev'),
#             state, read_bytes, write_bytes))
#
#         capacity, allocation, physical = domain.blockInfo(device.get('dev'))
#         print("VM_DiskUsage,name={},id={},uuid={},device={} state={},capacity={},allocation={},physical={}".format(
#             vm_name, id, vm_uuid, device.get('dev'),
#             state, capacity, allocation, physical))
#
#         # capacity : logical size in bytes of the image (how much storage the guest will see)
#         # allocation : host storage in bytes occupied by the image
#         # physical : host physical size in bytes of the image container
#     devices = root.findall('devices/memory')
#     for device in devices:
#         pmem_path, pmem_size = '', 0
#
#         memory_model = device.get('model')
#         children = device.getchildren()
#         for child in children:
#             if child.tag == 'source':
#                 pmem_path = child.getchildren()[0].text
#
#             if child.tag == 'target':
#                 for target_info in child.getchildren():
#                     if target_info.tag == "size":
#                         if target_info.get('unit') == 'KiB':
#                             pmem_size = int(target_info.text) * 1024
#                         else:
#                             pmem_size = int(target_info.text)
#
#
#         print('VM_PMEM,name={},id={},uuid={},model={} state={},path="{}",size={}'.format(
#             vm_name, id, vm_uuid, memory_model,
#             state, pmem_path, pmem_size
#             )
#
#         )
#         # capacity : logical size in bytes of the image (how much storage the guest will see)
#         # allocation : host storage in bytes occupied by the image
#         # physical : host physical size in bytes of the image container
#     network_interfaces = root.findall('devices/interface/target')
#     for interface in network_interfaces:
#         rx_bytes, rx_packets, rx_error, rx_drop, tx_bytes, tx_packets, tx_error, tx_drop = \
#             domain.interfaceStats(interface.get('dev'))
#         tmp = "rx_bytes={},rx_packets={},rx_error={},rx_drop={},tx_bytes={},tx_packets={},tx_error={},tx_drop={}".format(
#             rx_bytes, rx_packets, rx_error, rx_drop, tx_bytes, tx_packets, tx_error, tx_drop
#         )
#         print("VM_NetworkIO,name={},id={},uuid={},interface={} state={},".format(
#             vm_name, id, vm_uuid, interface.get('dev'), state) + tmp
#         )

