<template>
  <section>
    <!--页面title-->
    <strong class="title">{{$route.meta.title}}</strong>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <el-form :inline="true" @submit.native.prevent>
        <router-link to="" style="text-decoration: none;color: aliceblue;">
          <el-button class="return-list" @click="$router.back(-1)">
            <i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>返回
          </el-button>
        </router-link>
        <el-form-item style="margin-left: 35px" v-if="$store.getters.roles.includes('admin')">
          <el-button class="el-icon-plus" type="primary" @click="handleAdd"> 新增DB配置</el-button>
        </el-form-item>
      </el-form>
    </el-col>

    <!--DB列表-->
    <el-table :data="dbConfigs" :row-style="reportRowStyle" :row-class-name="ReportTableRow"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="15%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="dbType" label="DB类型" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createAt" label="创建时间" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createUser" label="创建者" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateTime" label="更新时间" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateUser" label="更新者" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="10%">
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.status" src="../../../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="50%">
        <template slot-scope="scope">
          <el-button type="primary" size="small">
            <router-link :to="{name:'DBEnvConnect',params:{db_config_id: scope.row._id}}" style="color: #fff">连接信息
            </router-link>
          </el-button>
          <el-button type="primary" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <!--          <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>-->
          <el-button type="info" size="small" :loading="statusChangeLoading"
                     @click="handleChangeStatus(scope.$index, scope.row)">
            {{scope.row.status===false?'启用':'禁用'}}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!--添加 界面-->
    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="formVisible"
               :close-on-click-modal="false"
               style="width: 60%; left: 20%">
      <el-form :model="form" :rules="formRules" ref="form" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input placeholder="请输入DB名称" v-model="form.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="DB类型" prop='dbType'>
          <el-select clearable v-model.trim="form.dbType" auto-complete="off">
            <el-option v-for="(item,index) in dbTypeOptions" :key="index+''" :label="item.name"
                       :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop='description'>
          <el-input placeholder="请输入DB描述..." type="textarea" :rows="5" v-model="form.description"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="formVisible = false">取消</el-button>
        <el-button type="primary" @click.native="submit" :loading="loading">提交</el-button>
      </div>
    </el-dialog>
  </section>
</template>

<script>
    import {addDBConfig, getDBConfigs, updateDBConfig} from "../../../../api/dbConfig";

    export default {
        name: "DBConfig",
        data() {
            return {
                dbConfigs: [],
                dbTypeOptions: [
                    {name: 'MongoDB', value: 'MongoDB'},
                    {name: 'MySQL', value: 'MySQL'}
                ],
                listLoading: false,
                statusChangeLoading: false,
                selects: [],//列表选中列

                titleMap: {
                    add: '新增DB配置',
                    edit: '编辑DB配置'
                },
                dialogStatus: '',
                formVisible: false,//dialog是否显示
                loading: false,
                formRules: {
                    name: [
                        {required: true, message: '请输入名称', trigger: 'blur'},
                        {min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur'}
                    ],
                    dbType: [
                        {required: true, message: '请选择DB类型', trigger: 'blur'}
                    ],
                    description: [
                        {required: false, message: '请输入描述', trigger: 'blur'},
                        {max: 1024, message: '不能超过1024个字符', trigger: 'blur'}
                    ]
                },
                //编辑界面数据
                form: {
                    name: '',
                    dbType: '',
                    description: ''
                },
                initForm: {
                    name: '',
                    dbType: '',
                    description: ''
                }
            }
        },
        methods: {
            // 获取环境列表
            queryDBConfigs(params) {
                this.listLoading = true;
                let self = this;
                let header = {};
                getDBConfigs(this.$route.params.project_id, params, header).then((res) => {
                    let {status, data} = res;
                    self.listLoading = false;
                    if (status === 'ok') {
                        self.totalNum = data.totalNum;
                        self.dbConfigs = data.rows
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: 'DB配置列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.listLoading = false;
                });
            },
            getDBConfigList() {
                let self = this;
                let params = {
                    projectId: self.$route.params.project_id
                };
                this.queryDBConfigs(params);
            },
            handleDel: function (index, row) {
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    this.listLoading = true;
                    let self = this;
                    let params = {
                        'isDeleted': true
                    };
                    let headers = {
                        "Content-Type": "application/json",
                    };
                    updateTestEnv(this.$route.params.project_id, row._id, params, headers).then(res => {
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.$message({
                                message: '删除成功',
                                center: true,
                                type: 'success'
                            })
                        } else {
                            self.$message.error({
                                message: data,
                                center: true,
                            })
                        }
                        self.getTestEnvList()
                    });
                });
            },
            handleChangeStatus: function (index, row) {
                let self = this;
                self.statusChangeLoading = true;
                let status = !row.status;
                let params = {
                    'status': status
                };
                let headers = {
                    "Content-Type": "application/json",
                };
                updateTestEnv(this.$route.params.project_id, row._id, params, headers).then(res => {
                    let {status, data} = res;
                    self.statusChangeLoading = false;
                    if (status === 'ok') {
                        self.$message({
                            message: '状态变更成功',
                            center: true,
                            type: 'success'
                        });
                        row.status = !row.status;
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                    self.getTestEnvList()
                }).catch(() => {
                    self.$message.error({
                        message: '环境状态更新失败,请稍后重试哦',
                        center: true
                    })
                    self.statusChangeLoading = false;
                    self.getTestEnvList()
                });
            },
            //显示新增界面
            handleAdd: function () {
                this.formVisible = true;
                this.form = Object.assign({}, this.form, this.initForm);
                this.dialogStatus = 'add';
            },
            //显示编辑界面
            handleEdit: function (index, row) {
                this.formVisible = true;
                this.form = Object.assign({}, this.form, row);
                this.dialogStatus = 'edit'
            },
            //提交修改
            submit: function () {
                let self = this;
                this.$refs.form.validate((valid) => {
                    if (valid) {
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.loading = true;
                            //NProgress.start();
                            let headers = {
                                "Content-Type": "application/json",
                            };
                            if (this.dialogStatus == 'add') {
                                let params = {
                                    name: self.form.name.trim(),
                                    dbType: self.form.dbType,
                                    description: self.form.description.trim(),
                                    createUser: this.$store.getters.email || 'anonymous'
                                };
                                addDBConfig(this.$route.params.project_id, params, headers).then((res) => {
                                    let {status, data} = res;
                                    self.loading = false;
                                    if (status === 'ok') {
                                        self.$message({
                                            message: '添加成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['form'].resetFields();
                                        self.formVisible = false;
                                        self.getDBConfigList()
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        });
                                        self.$refs['form'].resetFields();
                                        self.formVisible = false;
                                        self.getDBConfigList()
                                    }
                                })
                            } else if (this.dialogStatus == 'edit') {
                                let params = {
                                    name: self.form.name.trim(),
                                    dbType: self.form.dbType,
                                    description: self.form.description.trim(),
                                    lastUpdateUser: this.$store.getters.email || 'anonymous'
                                };
                                updateDBConfig(this.$route.params.project_id, self.form._id, params, headers).then(res => {
                                    let {status, data} = res;
                                    self.loading = false;
                                    if (status === 'ok') {
                                        self.$message({
                                            message: '修改成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['form'].resetFields();
                                        self.formVisible = false;
                                        self.getDBConfigList()
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        })
                                        self.getDBConfigList()
                                    }
                                })
                            } else {
                                self.$message.error({
                                    message: "系统出错",
                                    center: true,
                                });
                                self.getDBConfigList()
                            }
                        });
                    }
                });
            },
            selectsChange: function (selects) {
                this.selects = selects;
            },
            // 修改table tr行的背景色
            reportRowStyle({row, rowIndex}) {
                if (!(row.status === true))
                    return 'background-color: #DDDDDD'
                else {
                    return ''
                }
            },
            ReportTableRow({row, rowIndex}) {
                return 'reportTableRow';
            }
        },
        created() {
            this.getDBConfigList()
        }
    }
</script>

<style lang="scss" scoped>
  .title {
    width: 200px;
    float: left;
    color: #475669;
    font-size: 25px;
    margin: 10px 5px;
    font-family: Arial;
  }

  .return-list {
    margin-top: 0px;
    margin-bottom: 10px;
    margin-left: 20px;
    border-radius: 25px;
  }
</style>
