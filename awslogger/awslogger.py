import botocore.exceptions
import datetime
import logging 
import time

class CloudWatchLogsHandler(logging.Handler):
    def __init__(self, session, log_group_name="cloudops-cli", log_stream_prefix=None):
        """ Initializes the log handler
        Args:
            session - A boto3 session with region_name already defined.
            log_group_name - [string] A log group name.
            log_stream_prefix - [string] A prefix for the log streams.
        """ 

        logging.Handler.__init__(self)
        self._client = session.client("logs")
        self._log_group_name=log_group_name
        self._log_stream_prefix = log_stream_prefix
        self._log_stream_name= self._create_stream_name()
        self._sequence_token = ""
        self._sequence_token = self._get_sequence_token()
        # XXX: PoC
        self._buffer = { "messages": [], "last_flushed": time.time() }


    def emit(self, record):
        """ Send record to log stream
        Args:
            record - [string] Record to log
        """

        # Create new stream if needed
        name = self._create_stream_name()
        if name != self._log_stream_name:
            self._log_stream_name = name

        # Prepare log event
        msg = self.format(record)
        now = int(time.time()* 1000)
        params = { 
                    "logGroupName": self._log_group_name,
                    "logStreamName": self._log_stream_name,
                    "logEvents": [
                        {
                            "timestamp": now,
                            "message": msg 
                        } 
                    ]}
        if len(self._sequence_token) > 0:
            params.update({ "sequenceToken": self._sequence_token })

        # Put log event and update sequence token
        try:
            resp = self._client.put_log_events(**params)

            self._sequence_token = resp["nextSequenceToken"]
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                self._sequence_token = self._get_sequence_token()
                self.emit(record)
            else:
                print("Unable to put log event on log group %s in log stream %s" %
                            (self._log_group_name, self._log_stream_name))
                print(e)


    def _create_stream_name(self):
        """ 
        Create a stream name
        Joins the log_stream_prefix with today's date
        """
        # Prepare the stream name
        today = datetime.datetime.now().strftime("%Y%m%d")
        if self._log_stream_prefix:
            name = self._log_stream_prefix + today
        else:
            name = self._log_stream_name = today

        return(name)


    def _get_sequence_token(self):
        """ Get the current sequence token AND create the log group/stream
            if it doesn't exist.
        Returns:
            [string] Log stream sequence token.
        """
    
        create_stream = False
        # List streams in log group
        try:
            # XXX: Should we paginate this?
            resp = self._client.describe_log_streams(
                                    logGroupName=self._log_group_name,
                                    logStreamNamePrefix=self._log_stream_name,
                                    descending=True)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                create_stream = True

        # Create log group if it doesn't exist
        if create_stream is True:
            self._create_log_group()
            self._create_log_stream()
            return ""

        # Create stream OR grab latest stream and return sequence token
        if len(resp["logStreams"]) == 0:
            self._create_log_stream()
            return ""
        else:
            if "uploadSequenceToken" in resp["logStreams"][0]:
                return resp["logStreams"][0]["uploadSequenceToken"]
            else:
                return ""


    def _create_log_group(self):
        """ Create log group """
        # Try to create log group
        try:
            self._client.create_log_group(logGroupName=self._log_group_name)
        except botocore.exceptions.ClientError as e:
            print("Unable to create CloudWatch Logs Log Group. %s" %
                    self._log_group_name)
            raise(e)
        return


    def _create_log_stream(self):
        """ Create log stream """
        # Try to create log stream
        try:
            self._client.create_log_stream(
                                    logGroupName=self._log_group_name,
                                    logStreamName=self._log_stream_name)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print("Log group %s not found." % (self._log_group_name))
                raise(e)
            else:
                print("Unable to create log stream (%s) on log group %s." %
                    (self._log_stream_name, self._log_group_name))
                raise(e)
        return
