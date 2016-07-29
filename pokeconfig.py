import os
import logging

logger = logging.getLogger(__name__)

class Pokeconfig:
    # constants
    WALK_MILES_PER_SECOND = 0.0008333 # assumes 3mph (or 0.0008333 miles per second) walking speed
    WALK_METERS_PER_SECOND = 1.34112 # conversion from 3mph
    EXPIRE_BUFFER_SECONDS = 5 # if a pokemon expires in 5 seconds or less (includes negative/stale pokemon), dont send it
    DEFAULT_NUM_STEPS = 5
    DEFAULT_DISTANCE_UNIT = 'miles'

    # configured via env
    auth_service = None
    username = None
    password = None
    location_name = None
    rarity_limit = 3
    slack_webhook_url = None
    num_steps = DEFAULT_NUM_STEPS
    distance_unit = DEFAULT_DISTANCE_UNIT
    position = ()

    def load_config(self, config_path):
        is_local = False
        if not 'DYNO' in os.environ:
            is_local = True
            if not os.path.exists(config_path):
                logging.error('please create a .env file in this directory in order to run locally!')
                exit(-1)

        # used for local testing without starting up heroku
        if is_local:
            env = {}
            logger.info('running locally, reading config from %s', config_path)
            with open(config_path, 'r') as fp:
                for line in fp:
                    idx = line.index('=')
                    key = line[:idx]
                    value = line[idx + 1:].strip()
                    env[key] = value
        else:
            logger.info('running on heroku, reading config from environment')
            env = os.environ

        try:
            self.auth_service = str(env['AUTH_SERVICE'])
            self.username = str(env['USERNAME'])
            self.password = str(env['PASSWORD'])
            self.location_name = str(env['LOCATION_NAME'])
            self.rarity_limit = int(env['RARITY_LIMIT'])
            self.slack_webhook_url = str(env['SLACK_WEBHOOK_URL'])
            if 'NUM_STEPS' in env:
                self.num_steps = int(env['NUM_STEPS'])
            else:
                logging.warn('NUM_STEPS not defined defaulting to: %s', self.num_steps)
            if 'DISTANCE_UNIT' in env:
                self.distance_unit = str(env['DISTANCE_UNIT'])
            else:
                logging.warn('DISTANCE_UNIT not defined defaulting to: %s', self.distance_unit)
        except KeyError as ke:
            logging.error('key must be defined in config: %s!', ke)
            exit(-1)

        Pokeconfig._instance = self
        logger.info('loaded config with params')
        for key, value in vars(self).iteritems():
            if key == 'password':
                value = '****'
            logger.info('%s=%s', key, value)

    _instance = None
    @staticmethod
    def get():
        return Pokeconfig._instance
