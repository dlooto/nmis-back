# Generated by Django 2.0 on 2018-11-19 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hospitals', '0001_initial'),
        ('devices', '0001_initial'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='softwaredevice',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_software_devices', to='hospitals.Staff', verbose_name='修改人'),
        ),
        migrations.AddField(
            model_name='softwaredevice',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='software_devices', to='projects.ProjectPlan', verbose_name='所属项目'),
        ),
        migrations.AddField(
            model_name='repairorderrecord',
            name='operator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='operate_repair_order_record', to='hospitals.Staff', verbose_name='操作人'),
        ),
        migrations.AddField(
            model_name='repairorderrecord',
            name='receiver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hospitals.Staff', verbose_name='操作的接受方'),
        ),
        migrations.AddField(
            model_name='repairorderrecord',
            name='repair_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='devices.RepairOrder', verbose_name='报修单/维修单'),
        ),
        migrations.AddField(
            model_name='repairorder',
            name='applicant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='applied_repair_order', to='hospitals.Staff', verbose_name='报修人/申请人'),
        ),
        migrations.AddField(
            model_name='repairorder',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_repair_order', to='hospitals.Staff', verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='repairorder',
            name='fault_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='devices.FaultType', verbose_name='故障分类'),
        ),
        migrations.AddField(
            model_name='repairorder',
            name='maintainer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hospitals.Staff', verbose_name='维修工程师'),
        ),
        migrations.AddField(
            model_name='repairorder',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_repair_orders', to='hospitals.Staff', verbose_name='修改人'),
        ),
        migrations.AddField(
            model_name='repairorder',
            name='repair_devices',
            field=models.ManyToManyField(blank=True, related_name='repair_device_list', to='devices.AssertDevice', verbose_name='报修设备清单'),
        ),
        migrations.AddField(
            model_name='ordereddevice',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_ordered_devices', to='hospitals.Staff', verbose_name='修改人'),
        ),
        migrations.AddField(
            model_name='ordereddevice',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ordered_devices', to='projects.ProjectPlan', verbose_name='所属项目'),
        ),
        migrations.AddField(
            model_name='medicaldevicesix8cate',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_medical_device_cate', to='hospitals.Staff', verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='medicaldevicesix8cate',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_six8_cates', to='hospitals.Staff', verbose_name='修改人'),
        ),
        migrations.AddField(
            model_name='medicaldevicesix8cate',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='child_six8_cate', to='devices.MedicalDeviceSix8Cate', verbose_name='父级分类'),
        ),
        migrations.AddField(
            model_name='maintenanceplan',
            name='assert_devices',
            field=models.ManyToManyField(blank=True, related_name='plan_device_list', to='devices.AssertDevice', verbose_name='计划维保设备清单'),
        ),
        migrations.AddField(
            model_name='maintenanceplan',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_maintenance_plan', to='hospitals.Staff', verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='maintenanceplan',
            name='executor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='executed_maintenance_plan', to='hospitals.Staff', verbose_name='执行人'),
        ),
        migrations.AddField(
            model_name='maintenanceplan',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_maintenance_plans', to='hospitals.Staff', verbose_name='修改人'),
        ),
        migrations.AddField(
            model_name='maintenanceplan',
            name='places',
            field=models.ManyToManyField(blank=True, related_name='plan_place_ships', to='hospitals.HospitalAddress', verbose_name='维保地点列表'),
        ),
        migrations.AddField(
            model_name='faulttype',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_fault_type', to='hospitals.Staff', verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='faulttype',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_fault_types', to='hospitals.Staff', verbose_name='修改人'),
        ),
        migrations.AddField(
            model_name='faulttype',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='devices.FaultType', verbose_name='父类故障类型'),
        ),
        migrations.AddField(
            model_name='faultsolution',
            name='auditor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='audited_problem_solutions', to='hospitals.Staff', verbose_name='审核人'),
        ),
        migrations.AddField(
            model_name='faultsolution',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_problem_solutions', to='hospitals.Staff', verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='faultsolution',
            name='fault_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='related_problem_solution', to='devices.FaultType', verbose_name='故障/问题分类'),
        ),
        migrations.AddField(
            model_name='faultsolution',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_problem_solutions', to='hospitals.Staff', verbose_name='修改人'),
        ),
        migrations.AddField(
            model_name='contractdevice',
            name='contract',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contract_devices', to='projects.PurchaseContract', verbose_name='所属采购合同'),
        ),
        migrations.AddField(
            model_name='contractdevice',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_contract_devices', to='hospitals.Staff', verbose_name='修改人'),
        ),
        migrations.AddField(
            model_name='assertdevicerecord',
            name='assert_device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='devices.AssertDevice', verbose_name='资产设备'),
        ),
        migrations.AddField(
            model_name='assertdevicerecord',
            name='operator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='operate_assert_device_record', to='hospitals.Staff', verbose_name='操作人'),
        ),
        migrations.AddField(
            model_name='assertdevicerecord',
            name='receiver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hospitals.Staff', verbose_name='操作的接受方'),
        ),
        migrations.AddField(
            model_name='assertdevice',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_assert_device', to='hospitals.Staff', verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='assertdevice',
            name='medical_device_cate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='related_assert_device', to='devices.MedicalDeviceSix8Cate', verbose_name='医疗器械分类'),
        ),
        migrations.AddField(
            model_name='assertdevice',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_assert_devices', to='hospitals.Staff', verbose_name='修改人'),
        ),
        migrations.AddField(
            model_name='assertdevice',
            name='performer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='performed_assert_device', to='hospitals.Staff', verbose_name='资产负责人'),
        ),
        migrations.AddField(
            model_name='assertdevice',
            name='responsible_dept',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='responsible_assert_device', to='hospitals.Department', verbose_name='负责科室'),
        ),
        migrations.AddField(
            model_name='assertdevice',
            name='storage_place',
            field=models.ForeignKey(blank=True, null=True, on_delete='存放地点', to='hospitals.HospitalAddress'),
        ),
        migrations.AddField(
            model_name='assertdevice',
            name='use_dept',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='used_assert_device', to='hospitals.Department', verbose_name='使用科室'),
        ),
    ]
