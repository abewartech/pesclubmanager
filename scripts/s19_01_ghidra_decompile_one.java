// Ghidra headless: recursive-disassemble + decompile one function. v3.
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.util.task.ConsoleTaskMonitor;

public class DecompileOne extends GhidraScript {
    @Override
    public void run() throws Exception {
        long target = Long.decode(getScriptArgs()[0]);
        Address addr = currentProgram.getAddressFactory()
                .getDefaultAddressSpace().getAddress(target);

        // Proper recursive disassembly from entry point, following flows.
        DisassembleCommand cmd = new DisassembleCommand(addr, null, true);
        boolean ok = cmd.applyTo(currentProgram, monitor);
        println("DIAG recursive disasm ok=" + ok);

        Function func = getFunctionAt(addr);
        if (func == null) {
            createFunction(addr, null);
            func = getFunctionAt(addr);
        }
        if (func == null) {
            println("DIAG createFunction failed");
            return;
        }
        println("FUNCTION: " + func.getName() + " @ " + addr
                + " size=" + func.getBody().getNumAddresses());

        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        DecompileResults res = decomp.decompileFunction(func, 120,
                ConsoleTaskMonitor.DUMMY);
        if (res != null && res.getDecompiledFunction() != null) {
            println(res.getDecompiledFunction().getC());
        } else {
            println("DECOMPILE FAILED: "
                    + (res != null ? res.getErrorMessage() : "no result"));
        }
        decomp.dispose();
    }
}
