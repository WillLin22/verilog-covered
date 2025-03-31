`timescale 1 ps/1 ps

module testbench();
  reg clock;
  reg reset;
  reg [31:0] io_a;
  reg [2:0] io_rm;
  reg io_op;
  wire [31:0] io_result;
  wire [4:0] io_fflags;

  FPToInt fp2int_inst (
    // .clock(clock),
    // .reset(reset),
    .io_a(io_a),
    .io_rm(io_rm),
    .io_op(io_op),
    .io_result(io_result),
    .io_fflags(io_fflags)
  );

  initial begin
    bit [31:0] a;
	  bit [2:0] rm;
    bit op;
    // Initialize signals
    clock = 0;
    reset = 0;
    io_a = 0;
    io_rm = 0;
    op = 0;


    // Prompt for input
    $value$plusargs("rm=%x", rm);
    $value$plusargs("a=%x", a);
    $value$plusargs("op=%x", op);


    // Assign inputs
    io_a = a;
    io_rm = rm;
    io_op = op;

    // Wait for a few clock cycles
    #10;

    // Display results
    $display("rm: %x", rm);
    $display("a: %x", a);
    $display("op: %x", op);
    $display("io_rm: %x", io_rm);
    $display("io_a: %x", io_a);
    $display("io_op: %x", io_op);
    $display("io_result: %x", io_result);
    $display("io_fflags: %x", io_fflags);

    // End simulation
    $finish;
  end


endmodule
