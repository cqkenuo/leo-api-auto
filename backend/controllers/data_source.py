from datetime import datetime

from bson import ObjectId
from flask import jsonify, request
from flask_security import login_required

from app_init import app
from models.data_source import DBConfig, DBEnvConnect
from utils import common


@app.route('/api/project/<project_id>/dbConfigList', methods=['GET'])
@login_required
def db_config_list(project_id):
    total_num, dbs = common.get_total_num_and_arranged_data(DBConfig, request.args)
    return jsonify({'status': 'ok', 'data': {'totalNum': total_num, 'rows': dbs}})


@app.route('/api/project/<project_id>/dbConfig/<db_config_id>', methods=['GET'])
@login_required
def get_db_config(project_id, db_config_id):
    try:
        res = DBConfig.find_one({'_id': ObjectId(db_config_id)})
        return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)}) if res else \
            jsonify({'status': 'failed', 'data': '未找到该dbConfig信息'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '出错了 %s' % e})


@app.route('/api/project/<project_id>/addDBConfig', methods=['POST'])
@login_required
def add_db_config(project_id):
    try:
        request_data = request.get_json()
        request_data['status'] = True
        request_data['projectId'] = ObjectId(project_id)
        request_data['createAt'] = datetime.utcnow()
        filtered_data = DBConfig.filter_field(request_data, use_set_default=True)
        DBConfig.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '新增DB配置成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '新建失败 %s' % e})


@app.route('/api/project/<project_id>/updateDBConfig/<db_config_id>', methods=['POST'])
@login_required
def update_db_config(project_id, db_config_id):
    try:
        request_data = request.get_json()
        request_data['lastUpdateTime'] = datetime.utcnow()
        filtered_data = DBConfig.filter_field(request_data)
        update_response = DBConfig.update({'_id': ObjectId(db_config_id)}, {'$set': filtered_data})
        if update_response['n'] == 0:
            return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
        return jsonify({'status': 'ok', 'data': '更新DB配置成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '更新DB配置失败 %s' % e})


@app.route('/api/project/<project_id>/getDBEnvConnect', methods=['POST'])
@login_required
def get_db_env_connect(project_id):
    try:
        request_data = request.get_json()
        db_config_id = request_data['dbConfigId']
        test_env_id = request_data['testEnvId']
        if not db_config_id or not test_env_id:
            return jsonify({'status': 'failed', 'data': '参数不完整'})
        res = DBEnvConnect.find_one({'dbConfigId': ObjectId(db_config_id), 'testEnvId': ObjectId(test_env_id)})
        return jsonify({'status': 'ok', 'data': common.format_response_in_dic(res)}) if res else \
            jsonify({'status': 'ok', 'data': {'dbHost': ''}})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '出错了 %s' % e})


@app.route('/api/project/<project_id>/updateDBEnvConnect', methods=['POST'])
@login_required
def update_db_env_connect(project_id):
    try:
        request_data = request.get_json()
        print(request_data)
        if not request_data['dbConfigId'] or not request_data['testEnvId']:
            return jsonify({'status': 'failed', 'data': '参数不完整,dbConfigId/testEnvId'})
        request_data['dbConfigId'] = ObjectId(request_data['dbConfigId'])
        request_data['testEnvId'] = ObjectId(request_data['testEnvId'])
        db_config_id = request_data['dbConfigId']
        test_env_id = request_data['testEnvId']
        res = DBEnvConnect.find_one({'dbConfigId': ObjectId(db_config_id), 'testEnvId': ObjectId(test_env_id)})

        if res:
            request_data['lastUpdateTime'] = datetime.utcnow()
            filtered_data = DBEnvConnect.filter_field(request_data, use_set_default=True)
            update_response = DBEnvConnect.update(
                {'dbConfigId': ObjectId(db_config_id), 'testEnvId': ObjectId(test_env_id)}, {'$set': filtered_data})
            if update_response['n'] == 0:
                return jsonify({'status': 'failed', 'data': '未找到相应的更新数据！'})
            return jsonify({'status': 'ok', 'data': '更新DB连接配置成功'})
        else:
            request_data['createAt'] = datetime.utcnow()
            filtered_data = DBEnvConnect.filter_field(request_data, use_set_default=True)
            DBEnvConnect.insert(filtered_data)
        return jsonify({'status': 'ok', 'data': '更新DB连接配置成功'})
    except BaseException as e:
        return jsonify({'status': 'failed', 'data': '变更DB连接配置失败 %s' % e})


def get_db_connect(db_config_id, test_env_id):
    try:
        if not db_config_id or not test_env_id:
            return jsonify({'status': 'failed', 'data': '参数不完整'})
        res = DBEnvConnect.find_one({'dbConfigId': ObjectId(db_config_id), 'testEnvId': ObjectId(test_env_id)})
        return common.format_response_in_dic(res) if res else None
    except BaseException as e:
        return e
