// Frida script for PES Club Manager (offline/mock only).
// Load after libUE4.so is mapped, e.g.:
//   frida -U -f jp.konami.pesclubmanager -l scripts/frida_onlineapi_server_slot.js
// or attach:
//   frida -U jp.konami.pesclubmanager -l scripts/frida_onlineapi_server_slot.js
//
// Goal: record which server slot is read/selected at runtime.

function hookExport(name, callbacks) {
    const addr = Module.findExportByName("libUE4.so", name);
    if (!addr) {
        console.log("[!] export not found: " + name);
        return null;
    }
    console.log("[+] hooking " + name + " @ " + addr);
    Interceptor.attach(addr, callbacks);
    return addr;
}

function logPtr(label, ptr) {
    try {
        console.log(label + ": " + ptr);
    } catch (e) {
        console.log(label + ": <unreadable> " + e);
    }
}

// Init config-driven server selection.
hookExport("_ZN9onlineapi10ServerData4InitEv", {
    onEnter: function (args) {
        console.log("=== ServerData::Init() enter ===");
    },
    onLeave: function (retval) {
        const getApi = Module.findExportByName("libUE4.so", "_ZN9onlineapi10ServerData12GetAPIServerEv");
        if (getApi) {
            const fn = new NativeFunction(getApi, "int", []);
            console.log("=== ServerData::Init() leave; GetAPIServer()=" + fn() + " ===");
        }
    }
});

// Active download slot write.
hookExport("_ZN9onlineapi10ServerData17SetDownloadServerENS0_11SERVER_CODEE", {
    onEnter: function (args) {
        console.log("=== SetDownloadServer(slot=" + args[0].toInt32() + ") ===");
    }
});

// Resource URL read path. arg0=this, arg1=char*, arg2=SERVER_CODE.
hookExport("_ZN9onlineapi10ServerData14GetResourceUrlEPKcNS0_11SERVER_CODEE", {
    onEnter: function (args) {
        this.path = (args[1].isNull() ? "<null>" : Memory.readUtf8String(args[1]));
        this.slotArg = args[2].toInt32();
        console.log("=== GetResourceUrl(path=" + this.path + ", slotArg=" + this.slotArg + ") ===");
    },
    onLeave: function (retval) {
        try {
            console.log("    result=" + (retval.isNull() ? "<null>" : Memory.readUtf8String(retval)));
        } catch (e) {
            console.log("    result=<not utf8> " + e);
        }
    }
});

// Optional: download-server change path.
const change = Module.findExportByName("libUE4.so", "_ZN9onlineapi10ServerData20ChangeDownloadServerEiPKc");
if (change) {
    Interceptor.attach(change, {
        onEnter: function (args) {
            console.log("=== ChangeDownloadServer(slot=" + args[0].toInt32() + ", host=" + (args[1].isNull() ? "<null>" : Memory.readUtf8String(args[1])) + ") ===");
        }
    });
} else {
    console.log("[!] ChangeDownloadServer not found");
}

console.log("[*] hooks installed");
