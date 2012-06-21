//Copyright (c) 2012, Carnegie Mellon University.
//All rights reserved.
//
//Redistribution and use in source and binary forms, with or without
//modification, are permitted provided that the following conditions
//are met:
//1. Redistributions of source code must retain the above copyright
//   notice, this list of conditions and the following disclaimer.
//2. Redistributions in binary form must reproduce the above copyright
//   notice, this list of conditions and the following disclaimer in the
//   documentation and/or other materials provided with the distribution.
//3. Neither the name of the University nor the names of its contributors
//   may be used to endorse or promote products derived from this software
//   without specific prior written permission.

/**
 * Machines / attributes selector
 * @author ishafer
 */

var SOURCES = [
    {host:"172.19.159.3",port:4242,
        name:"Hadoop OpenTSDB",
        getAttrNames: function() {
            return[
                "iostat.disk.read_requests",
                "iostat.disk.write_requests",
                "iostat.disk.msec_write",
                "iostat.disk.msec_read",
                "iostat.disk.read_sectors",
                "iostat.disk.write_sectors",
                "proc.stat.cpu,type.system",
                "proc.stat.cpu,type.user",
                "proc.stat.cpu,type.iowait",
                "proc.stat.cpu,type.nice",
                "proc.net.bytes,direction.in",
                "proc.net.bytes,direction.out",
                "proc.net.packets,direction.in",
                "proc.net.packets,direction.out",
                "proc.loadavg.runnable",
                "proc.meminfo.memfree",
                "proc.meminfo.memtotal",
                "proc.meminfo.cached",
                "proc.meminfo.buffers",
                "proc.stat.ctxt",
                "proc.stat.intr",
                "proc.stat.procs_blocked",
                "proc.loadavg.total_threads"
            ];
        },
        getCompNames: function() {
            var names = [];
            for (var i = 0; i < 64; ++i) {
                var name = (i+1) + "";
                if (name.length < 2) {
                    name = "0" + name;
                }
                names.push(name);
            }        
            return names;   
        },
        getCompSel: function(i,el) {return i < 16;},
        getAttrSel: function(i,el) {return i < 2;},
        compcols:4,
        cloudifyNames:true
    },
    {host:"172.19.149.159",port:8000,
        name:"CMU.net RRD",
        getAttrNames: function() {
            var names = ["median","loss","uptime"];
            for (var i = 0; i < 16; ++i) {
                names.push("ping" + (i+1));
            }
            return names;
        },
        getCompNames: function() {
            return [
                "CMU-West",
                "LocalMachine",
                "NewYork",
                "PSU",
                "QatarExternal",
                "Qatar"
            ];
        },
        getCompSel: function(i,el) {return i < 12;},
        getAttrSel: function(i,el) {return i < 1;},
        compcols:1,
        cloudifyNames:false
    },    
    {host:"172.19.159.3",port:8123,
        name:"Hadoop Ganglia",
        getAttrNames: function() {
            var names = ['bytes_in', 'bytes_out', 'pkts_in', 'pkts_out', 'cpu_aidle', 'cpu_idle', 'cpu_nice', 'cpu_num', 'cpu_speed', 'cpu_system', 'cpu_user', 'cpu_wio', 'disk_bytes_read', 'disk_bytes_write', 'disk_free', 'disk_req_read', 'disk_req_write', 'disk_total', 'mem_buffers', 'mem_cached', 'mem_free', 'mem_shared', 'mem_total', 'page_fault', 'page_in', 'page_major_fault', 'page_out', 'slab_memory_reclaimable', 'slab_memory', 'slab_memory_unreclaimable', 'swap_free', 'swap_in', 'swap_out', 'swap_total', 'vmem_committed_percentage', 'vmem_committed', 'dfs.datanode.blockChecksumOp_avg_time', 'dfs.datanode.blockChecksumOp_num_ops', 'dfs.datanode.blockReports_avg_time', 'dfs.datanode.blockReports_num_ops', 'dfs.datanode.blocks_read', 'dfs.datanode.blocks_removed', 'dfs.datanode.blocks_replicated', 'dfs.datanode.blocks_verified', 'dfs.datanode.blocks_written', 'dfs.datanode.block_verification_failures', 'dfs.datanode.bytes_read', 'dfs.datanode.bytes_written', 'dfs.datanode.copyBlockOp_avg_time', 'dfs.datanode.copyBlockOp_num_ops', 'dfs.datanode.heartBeats_avg_time', 'dfs.datanode.heartBeats_num_ops', 'dfs.datanode.readBlockOp_avg_time', 'dfs.datanode.readBlockOp_num_ops', 'dfs.datanode.readMetadataOp_avg_time', 'dfs.datanode.readMetadataOp_num_ops', 'dfs.datanode.reads_from_local_client', 'dfs.datanode.reads_from_remote_client', 'dfs.datanode.replaceBlockOp_avg_time', 'dfs.datanode.replaceBlockOp_num_ops', 'dfs.datanode.writeBlockOp_avg_time', 'dfs.datanode.writeBlockOp_num_ops', 'dfs.datanode.writes_from_local_client', 'dfs.datanode.writes_from_remote_client', 'mapred.tasktracker.maps_running', 'mapred.tasktracker.mapTaskSlots', 'mapred.tasktracker.reduces_running', 'mapred.tasktracker.reduceTaskSlots', 'mapred.tasktracker.tasks_completed', 'mapred.tasktracker.tasks_failed_ping', 'mapred.tasktracker.tasks_failed_timeout', 'boottime', 'proc_run', 'proc_total', 'load_fifteen', 'load_five', 'load_one'];
            return names;
        },
        getCompNames: function() {
            var names = [];
            for (var i = 0; i < 64; ++i) {
                var name = (i+1) + "";
                if (name.length < 2) {
                    name = "0" + name;
                }
                names.push(name);
            }        
            return names;   
           
        },
        getCompSel: function(i,el) {return i < 12;},
        getAttrSel: function(i,el) {return i < 1;},
        compcols:1,
        cloudifyNames:true
    },    

];

Selector = {};
Selector.source = null;
Selector.compnames = [];
Selector.attrnames = [];
Selector.loadCompNames = function() {
    Selector.compnames = Selector.source.getCompNames();
}
Selector.loadAttrNames = function() {
    Selector.attrnames = Selector.source.getAttrNames();
}
/**
 * @param fn(i,el) callback: should box with index i and value el be checked?
 */
Selector.setChecked = function(cont, fn) {
    $("#" + cont + " input").each(function(i, el) {
        $(el)[fn(i, el) ? "attr" : "removeAttr"]("checked", "checked");
        $(el).button("refresh");
    });   
}
Selector.setAllCheck = function(cont, state) {
    Selector.setChecked(cont, function(i,el) { return state; });
};
Selector.init = function() {
    Selector.initSourceSel(SOURCES);

    Selector.loadSource(Options.get("source.id"));

    $("#sel-area").accordion({
        fillSpace: true,
        collapsible: true
    });
}
Selector.loadSource = function(name) {
    Selector.source = SOURCES[name];

    Selector.loadCompNames();
    Selector.initCompSel(Selector.compnames);
    //Selector.setAllCheck("compsel", true);
    Selector.setChecked("compsel", Selector.source.getCompSel);

    Selector.loadAttrNames();
    Selector.initAttrSel(Selector.attrnames);
    //Selector.setAllCheck("attrsel", true);
    Selector.setChecked("attrsel", Selector.source.getAttrSel);
}
/**
 * Create an input selector with id sel-{id}, label {name}, and append it to {cont}
 */
Selector.initSourceSel = function(sources) {
    $("#sourcessel").empty();
    var inner = $("<form>").css({"font-size":"0.6em"});
    $.each(sources, function(i, source) {
        var inpt = $("<input>").attr({
            "type":"radio",
            "name":"sourcegroup",
            "value":i
        });
        inpt.change(function() {
            var sourcename = $(this).val();
            Selector.loadSource(sourcename);
        })
        inner.append(
            $("<div>")
                .append(inpt)
                .append(source.name)
                .css({"font-size":"1.4em"})
            );
        inner.append($("<div>").text("nodes: " + source.getCompNames().length));
        inner.append($("<div>").text("metrics: " + source.getAttrNames().length));
        var hostdisp = source.host;
        if (hostdisp.length > 15) {
            hostdisp = hostdisp.substring(0,15) + "...";
        }
        inner.append($("<div>").text("host: " + hostdisp));
        
        if (i == Options.get("source.id")) {
            inpt.attr("checked","checked");
        }
    });
    $("#sourcessel").append(inner);
};
Selector.addinpt = function(cont, id, name) {
    $("<input/>")
        .attr("type","checkbox")
        .attr("id","sel-" + id)
        .data("name",name)
        .appendTo(cont);
    $("<label>")
        .text(name)
        .attr("for","sel-" + id)
        .appendTo(cont);    
}
Selector.initCompSel = function(compnames) {
    $("#compsel").empty();
    var tbl = $("<table>").appendTo("#compsel");
    var curtr;
    $.each(compnames, function(i, el) {
        if (i % Selector.source.compcols == 0) {
            curtr = $("<tr>").appendTo(tbl);
        }
        var cstd = $("<td>");
        Selector.addinpt(cstd, "comp-" + i, el);
        cstd.appendTo(curtr);
    });
    $("#compsel input").each(function(i, el) {
        $(el).button();
    });
    $("#btn-csall")
        .button({icons:{primary:"ui-icon-check"}})
        .click(function() {
            Selector.setAllCheck("compsel", true);
        });
    $("#btn-csnone")
        .button({icons:{primary:"ui-icon-minusthick"}})
        .click(function() {
            Selector.setAllCheck("compsel", false);
        });
};
Selector.initAttrSel = function(attrnames) {
    var cont = $("#attrsel");
    cont.empty();
    $.each(attrnames, function(i, el) {
        var adiv = $("<div>");
        Selector.addinpt(adiv, "attr-" + i, el);
        adiv.appendTo(cont);
    });
    $("#attrsel input").each(function(i, el) {
        $(el).button();
    }); 
}
/**
 * Get selected togglebuttons in container {cont}
 */
Selector.getSelected = function(cont) {
    var seled = [];
    $("#" + cont + " input").each(function(i, el) {
        if ($(el).attr("checked")) {
            seled.push($(el).data("name"));
        }
    });
    return seled;
};
