# Generated by Django 2.0 on 2018-11-19 15:06

from django.db import migrations, models
import django.db.models.deletion

from settings import SET_PROJECT_START_ID


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hospitals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('title', models.CharField(max_length=30, verbose_name='里程碑标题')),
                ('index', models.SmallIntegerField(default=1, verbose_name='索引顺序')),
                ('desc', models.CharField(default='', max_length=30, verbose_name='描述')),
                ('parent_path', models.CharField(default='', max_length=255, verbose_name='父里程碑路径')),
                ('modified_time', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
            ],
            options={
                'verbose_name': '里程碑项',
                'verbose_name_plural': '里程碑项',
                'db_table': 'projects_milestone',
                'ordering': ['index'],
                'permissions': (('view_milestone', 'can view milestone'),),
            },
        ),
        migrations.CreateModel(
            name='ProjectDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('name', models.CharField(max_length=100, verbose_name='文档名称')),
                ('category', models.CharField(choices=[('product', '产品资料'), ('producer', '厂商资料'), ('supplier_selection_plan', '供应商选择方案'), ('plan_argument', '方案论证资料'), ('decision_argument', '决策论证'), ('bidding_doc', '招标文件'), ('tender_doc', '投标文件'), ('purchase_plan', '采购计划'), ('contract', '合同'), ('delivery_note', '送货单'), ('implement_plan', '实施方案'), ('implement_record', '实施日志'), ('implement_summary', '实施总结'), ('acceptance_plan', '验收方案'), ('acceptance_report', '验收报告'), ('others', '其他资料')], max_length=30, verbose_name='文档类别')),
                ('path', models.CharField(max_length=255, verbose_name='存放路径')),
            ],
            options={
                'verbose_name': '文档资料',
                'verbose_name_plural': '文档资料',
                'db_table': 'projects_project_document',
            },
        ),
        migrations.CreateModel(
            name='ProjectFlow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('title', models.CharField(default='默认', max_length=30, verbose_name='流程名称')),
                ('type', models.CharField(blank=True, default='', max_length=10, null=True, verbose_name='流程类型')),
                ('pre_defined', models.BooleanField(default=False, verbose_name='是否预定义')),
                ('default_flow', models.BooleanField(default=False, verbose_name='是否为默认流程')),
                ('modified_time', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('modifier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_flows', to='hospitals.Staff', verbose_name='修改人')),
                ('organ', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospitals.Hospital', verbose_name='所属医院')),
            ],
            options={
                'verbose_name': 'B 项目流程',
                'verbose_name_plural': 'B 项目流程',
                'db_table': 'projects_project_flow',
                'permissions': (('view_project_flow', 'can view project flow'),),
            },
        ),
        migrations.CreateModel(
            name='ProjectMilestoneState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('doc_list', models.CharField(blank=True, max_length=100, null=True, verbose_name='文档列表')),
                ('summary', models.TextField(blank=True, max_length=1024, null=True, verbose_name='总结说明')),
                ('status', models.CharField(choices=[('TODO', '未开始'), ('DOING', '进行中'), ('DONE', '已完结')], default='TODO', max_length=10, verbose_name='项目里程碑状态')),
                ('finished_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='项目里程碑完结时间')),
                ('modified_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='最近一次修改时间')),
                ('milestone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pro_milestone_states_related', to='projects.Milestone', verbose_name='里程碑节点')),
            ],
            options={
                'verbose_name': '项目里程碑',
                'verbose_name_plural': '项目里程碑',
                'db_table': 'projects_project_milestone_state',
                'permissions': (('view_project_milestone_state', 'can view project milestone state'),),
            },
        ),
        migrations.CreateModel(
            name='ProjectOperationRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('project', models.IntegerField(verbose_name='项目')),
                ('reason', models.TextField(verbose_name='原因')),
                ('operation', models.CharField(choices=[('overrule', '驳回'), ('pause', '挂起')], max_length=10, verbose_name='操作方式')),
            ],
            options={
                'verbose_name': '项目操作日志',
                'verbose_name_plural': '项目操作日志',
                'db_table': 'projects_operation_record',
                'permissions': (('view_project_operation_record', 'can view project operation record'),),
            },
        ),
        migrations.CreateModel(
            name='ProjectPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('title', models.CharField(max_length=50, verbose_name='项目名称')),
                ('handing_type', models.CharField(choices=[('SE', '自行办理'), ('AG', '转交办理')], default='SE', max_length=10, verbose_name='办理方式')),
                ('purpose', models.CharField(default='', max_length=255, null=True, verbose_name='申请原因')),
                ('status', models.CharField(choices=[('PE', '未开始'), ('SD', '已启动'), ('DO', '已完成'), ('OR', '已驳回'), ('PA', '已挂起')], default='PE', max_length=10, verbose_name='项目状态')),
                ('startup_time', models.DateTimeField(blank=True, null=True, verbose_name='项目启动时间')),
                ('expired_time', models.DateTimeField(blank=True, null=True, verbose_name='项目截止时间')),
                ('project_cate', models.CharField(choices=[('SW', '信息化项目'), ('HW', '医疗器械项目')], default='HW', max_length=10, verbose_name='项目类型')),
                ('project_introduce', models.CharField(blank=True, max_length=200, null=True, verbose_name='项目介绍/项目描述')),
                ('pre_amount', models.FloatField(blank=True, null=True, verbose_name='项目预估总价')),
                ('purchase_method', models.CharField(blank=True, choices=[('OPEN', '公开招标'), ('INVITED', '邀请招标/选择性招标'), ('COMPETITIVE', '竞争性谈判/协商招标'), ('SINGE', '单一来源采购'), ('INQUIRY', '询价采购')], max_length=20, null=True, verbose_name='采购方式')),
                ('finished_time', models.DateTimeField(blank=True, null=True, verbose_name='项目实际完结时间')),
                ('modified_time', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('assistant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assisted_projects', to='hospitals.Staff', verbose_name='协助办理人')),
                ('attached_flow', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='projects.ProjectFlow', verbose_name='项目使用的流程')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_projects', to='hospitals.Staff', verbose_name='项目申请人/提出者')),
                ('current_stone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='projects.ProjectMilestoneState', verbose_name='项目里程碑节点')),
                ('modifier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_projects', to='hospitals.Staff', verbose_name='修改人')),
                ('performer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='performed_projects', to='hospitals.Staff', verbose_name='项目负责人/执行人')),
                ('pro_milestone_states', models.ManyToManyField(blank=True, related_name='projects', related_query_name='project', through='projects.ProjectMilestoneState', to='projects.Milestone', verbose_name='项目里程碑')),
                ('related_dept', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hospitals.Department', verbose_name='申请科室')),
            ],
            options={
                'verbose_name': 'A 项目申请',
                'verbose_name_plural': 'A 项目申请',
                'db_table': 'projects_project_plan',
                'permissions': (('view_project_plan', 'can view project plan'), ('dispatch_project_plan', 'can dispatch project plan'), ('overrule_project_plan', 'can overrule project plan'), ('pause_project_plan', 'can pause project plan'), ('startup_project_plan', 'can startup project plan')),
            },
        ),
        migrations.CreateModel(
            name='PurchaseContract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('contract_no', models.CharField(max_length=30, verbose_name='合同编号')),
                ('title', models.CharField(max_length=100, verbose_name='合同名称')),
                ('signed_date', models.DateField(verbose_name='签订时间')),
                ('buyer', models.CharField(max_length=128, verbose_name='买方/甲方单位')),
                ('buyer_contact', models.CharField(max_length=50, verbose_name='买方/甲方联系人')),
                ('buyer_tel', models.CharField(max_length=20, verbose_name='买方/甲方联系电话')),
                ('seller', models.CharField(max_length=128, verbose_name='卖方/乙方单位')),
                ('seller_contact', models.CharField(max_length=50, verbose_name='卖方/乙方联系人')),
                ('seller_tel', models.CharField(max_length=20, verbose_name='卖方/乙方联系电话')),
                ('total_amount', models.FloatField(default=0.0, verbose_name='合同总价')),
                ('delivery_date', models.DateField(verbose_name='交货时间')),
                ('doc_list', models.CharField(max_length=255, verbose_name='合同文档列表')),
                ('modified_time', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('project_milestone_state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.ProjectMilestoneState', verbose_name='所属项目里程碑子节点')),
            ],
            options={
                'verbose_name': '采购合同',
                'verbose_name_plural': '采购合同',
                'db_table': 'projects_purchase_contract',
                'permissions': (('view_purchase_contract', 'can view supplier purchase contract'),),
            },
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('served_date', models.DateField(blank=True, null=True, verbose_name='到货时间')),
                ('delivery_man', models.CharField(blank=True, max_length=50, null=True, verbose_name='送货人')),
                ('contact_phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='联系电话')),
                ('doc_list', models.CharField(blank=True, max_length=10, null=True, verbose_name='送货单附件')),
                ('modified_time', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('project_milestone_state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.ProjectMilestoneState', verbose_name='所属项目里程碑子节点')),
            ],
            options={
                'verbose_name': '收货确认单',
                'verbose_name_plural': '收货确认单',
                'db_table': 'projects_receipt',
                'permissions': (('view_receipt', 'can view receipt'),),
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('name', models.CharField(max_length=100, verbose_name='供应商名称')),
                ('contact', models.CharField(blank=True, max_length=50, null=True, verbose_name='联系人')),
                ('contact_tel', models.CharField(blank=True, max_length=20, null=True, verbose_name='联系电话')),
            ],
            options={
                'verbose_name': '供应商',
                'verbose_name_plural': '供应商',
                'db_table': 'projects_supplier',
                'permissions': (('view_supplier', 'can view supplier'),),
            },
        ),
        migrations.CreateModel(
            name='SupplierSelectionPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('total_amount', models.FloatField(default=0.0, verbose_name='方案总价')),
                ('remark', models.CharField(blank=True, max_length=254, null=True, verbose_name='备注')),
                ('doc_list', models.CharField(blank=True, max_length=32, null=True, verbose_name='方案文档列表')),
                ('selected', models.BooleanField(default=False, verbose_name='是否为最终选定方案')),
                ('modified_time', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('project_milestone_state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.ProjectMilestoneState', verbose_name='所属项目里程碑子节点')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Supplier', verbose_name='供应商')),
            ],
            options={
                'verbose_name': '供应商选择方案',
                'verbose_name_plural': '供应商选择方案',
                'db_table': 'projects_supplier_selection_plan',
                'permissions': (('view_supplier_selection_plan', 'can view supplier selection plan'),),
            },
        ),
        migrations.AddField(
            model_name='projectmilestonestate',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pro_milestone_states_related', to='projects.ProjectPlan', verbose_name='项目'),
        ),
        migrations.AddField(
            model_name='milestone',
            name='flow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='projects.ProjectFlow', verbose_name='归属流程'),
        ),
        migrations.AddField(
            model_name='milestone',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_milestones', to='hospitals.Staff', verbose_name='修改人'),
        ),
        migrations.AddField(
            model_name='milestone',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.Milestone', verbose_name='父里程碑'),
        ),
        migrations.AlterUniqueTogether(
            name='projectmilestonestate',
            unique_together={('project', 'milestone')},
        ),

        # customized id start
        migrations.RunSQL(  # id自增从设定的值开始
            SET_PROJECT_START_ID,
        ),
    ]
