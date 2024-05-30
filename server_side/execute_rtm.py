from consts import *
import subprocess
import os
import folder_scan
import filesUtil
import threading
import file_content_manipulation


def execute_rtm_engine():
    process_rtm_downloads = subprocess.Popen(
        [RTM_PATH, "downloads"],
        stdout=subprocess.PIPE, universal_newlines=True)

    process_rtm_windows = subprocess.Popen(
        [RTM_PATH, "windows"],
        stdout=subprocess.PIPE, universal_newlines=True)
    rtm_list = [process_rtm_windows, process_rtm_downloads]

    def read_output(process_rtm):
        infected_file = ""
        while True:
            output_line = process_rtm.stdout.readline().rstrip()
            if output_line == '' and process_rtm.poll() is not None:
                break
            if output_line:
                print(output_line)
                if not os.path.exists(output_line) or os.path.isdir(output_line):
                    continue
                if output_line.endswith(".tmp") or output_line.endswith("crdownload") or output_line.endswith("xml~"):
                    continue
                for file in folder_scan.scan([output_line]):
                    infected_file = file
                if infected_file:
                    file_content_manipulation.move_to_quarantine(infected_file)
        process_rtm_downloads.stdout.close()

        # Start reading output in a separate thread

    for i in rtm_list:
        output_reader = threading.Thread(target=read_output, args=[i])
        output_reader.daemon = True  # Daemonize the thread, so it terminates when the main thread terminates
        output_reader.start()
