import trace_gen_wrapper as tg
import sram_traffic as sram
import dram_trace as dram
import os
import subprocess


def run_net( ifmap_sram_size=1,
             filter_sram_size=1,
             ofmap_sram_size=1,
             array_h=32,
             array_w=32,
             topology_file = './topologies/yolo_v2.csv',
             net_name='yolo_v2'
            ):

    ifmap_sram_size *= 1024
    filter_sram_size *= 1024
    ofmap_sram_size *= 1024

    #fname = net_name + ".csv"
    param_file = open(topology_file, 'r')

    fname = net_name + "_avg_bw.csv"
    bw = open(fname, 'w')

    f2name = net_name + "_max_bw.csv"
    maxbw = open(f2name, 'w')

    f3name = net_name + "_cycles.csv"
    cycl = open(f3name, 'w')

    bw.write("IFMAP SRAM Size,\tFilter SRAM Size,\tOFMAP SRAM Size,\tConv Layer Num,\tDRAM IFMAP Read BW,\tDRAM Filter Read BW,\tDRAM OFMAP Write BW,\tSRAM OFMAP Write BW, \n")
    maxbw.write("IFMAP SRAM Size,\tFilter SRAM Size,\tOFMAP SRAM Size,\tConv Layer Num,\tMax DRAM IFMAP Read BW,\tMax DRAM Filter Read BW,\tMax DRAM OFMAP Write BW,\tMax SRAM OFMAP Write BW,\n")
    cycl.write("Layer,\tCycles,\n")

    first = True
    
    for row in param_file:
        if first:
            first = False
            continue
            
        elems = row.strip().split(',')
        #print(len(elems))
        
        # Do not continue if incomplete line
        if len(elems) < 9:
            continue

        name = elems[0]
        print("")
        print("Commencing run for " + name)

        ifmap_h = int(elems[1])
        ifmap_w = int(elems[2])

        filt_h = int(elems[3])
        filt_w = int(elems[4])

        num_channels = int(elems[5])
        num_filters = int(elems[6])

        strides = int(elems[7])
        filter_base = 1000000 * 100

        bw_log = str(ifmap_sram_size) +", " + str(filter_sram_size) + ", " + str(ofmap_sram_size) + ", " + name + ", "
        max_bw_log = bw_log

        bw_log += tg.gen_all_traces(array_h = array_h,
                                    array_w = array_w,
                                    ifmap_h = ifmap_h, 
                                    ifmap_w = ifmap_w,
                                    filt_h = filt_h, 
                                    filt_w = filt_w,
                                    num_channels = num_channels, 
                                    num_filt = num_filters,
                                    strides = strides,
                                    word_size_bytes = 1,
                                    filter_sram_size = filter_sram_size, 
                                    ifmap_sram_size = ifmap_sram_size, 
                                    ofmap_sram_size = ofmap_sram_size,
                                    filt_base =  filter_base,
                                    sram_read_trace_file= net_name + "_" + name + "_sram_read.csv",
                                    sram_write_trace_file= net_name + "_" + name + "_sram_write.csv",
                                    dram_filter_trace_file=net_name + "_" + name + "_dram_filter_read.csv",
                                    dram_ifmap_trace_file= net_name + "_" + name + "_dram_ifmap_read.csv",
                                    dram_ofmap_trace_file= net_name + "_" + name + "_dram_ofmap_write.csv"
                                    )

        bw.write(bw_log + "\n")

        max_bw_log += tg.gen_max_bw_numbers(
                                sram_write_trace_file= net_name + "_" + name + "_sram_write.csv",
                                dram_filter_trace_file=net_name + "_" + name + "_dram_filter_read.csv",
                                dram_ifmap_trace_file= net_name + "_" + name + "_dram_ifmap_read.csv",
                                dram_ofmap_trace_file= net_name + "_" + name + "_dram_ofmap_write.csv"
                                )

        maxbw.write(max_bw_log + "\n")

        last_line = subprocess.check_output(["tail","-1", net_name + "_" + name + "_sram_write.csv"] )
        clk = str(last_line).split(',')[0]
        clk = str(clk).split("'")[1]
        line = name + ",\t" + clk + ",\n"
        cycl.write(line)

    bw.close()
    maxbw.close()
    cycl.close()
    param_file.close()

#if __name__ == "__main__":
#    sweep_parameter_space_fast()    

