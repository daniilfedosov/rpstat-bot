import yaml
import sys
import metacheck

PROJECT = 'reactivecloud'
QUESTION = 16


def metabase_env():
    config = yaml.safe_load(open(sys.path[0] + '/env.yml'))
    return config['environment']


def metabase(env, session=None):
    session_id = metacheck.Base(env=env, session=session, project=PROJECT).session
    print(session_id)
    base = metacheck.Base(session=session_id, env=env, project=PROJECT)
    return base


def rate():
    env = metabase_env()
    base = metabase(env)
    count = (base.post('/card/%s/query/json' % QUESTION))[1]
    return count


result = rate()
print(result[0]['Count'])

