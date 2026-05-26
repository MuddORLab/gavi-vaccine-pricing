import logging
import xmlrpc.client as xmlrpclib


class NEOSConnection():
    """Encapsulate a connection to the NEOS server"""

    def __init__(self, neos_email, neos_host, neos_port, verbose=False):
        self.neos_email = neos_email
        self.neos_host = neos_host
        self.neos_port = neos_port
        self.verbose = verbose

    def create_xml_text(self, mod_text, dat_text, commands_text): # can set up to use baron then gurobi for example, pass the options/settings for each here
        return (
            "<document>\n"
            "<category>minco</category>\n"
            "<solver>GUROBI</solver>\n" # change solver here
            "<inputMethod>AMPL</inputMethod>\n"
            f"<email>{self.neos_email}</email>\n"
            "<model><![CDATA[\n"
            f"{mod_text}\n"
            "]]></model>\n"
            "<data><![CDATA[\n"
            f"{dat_text}\n"
            "]]></data>\n"
            "<commands><![CDATA[\n"
            f"{commands_text}\n"
            "]]></commands>\n"
            "</document>"
        )

    def submit_job(self, mod_text, dat_text, commands_text):
        # Create and submit job to NEOS
        self.conn = xmlrpclib.Server("https://{}:{}".format(
            self.neos_host,
            self.neos_port
        ))
        xml_text = self.create_xml_text(mod_text, dat_text, commands_text)
        self.job_number, self.password = self.conn.submitJob(xml_text)

        # Log job info
        if self.verbose:
            logging.info(f"Job number: {self.job_number}")
            logging.info(f"Password:   {self.password}")

    def wait_for_job(self):
        offset = 0
        status = None
        while status != "Done":
            msg, offset = self.conn.getIntermediateResults(
                self.job_number, self.password, offset
            )
            msg_text = msg.data.decode()
            if self.verbose:
                logging.info(f"Received data: {msg_text}")
            status = self.conn.getJobStatus(self.job_number, self.password)

    def get_final_results(self):
        msg = self.conn.getFinalResults(self.job_number, self.password)
        msg_text = msg.data.decode()
        if self.verbose:
            logging.info(f"Received data: {msg_text}")
        return msg_text
