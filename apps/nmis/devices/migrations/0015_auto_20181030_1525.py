# Generated by Django 2.0 on 2018-10-30 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0014_merge_20181030_1408'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assertdevice',
            options={'permissions': (('view_assert_device', 'can view assert device'), ('scrap_assert_device', 'can scrap assert device'), ('allocate_assert_device', 'can allocate assert device'), ('import_fault_solution', 'can import fault_solution')), 'verbose_name': '资产设备', 'verbose_name_plural': '资产设备'},
        ),
        migrations.AlterModelOptions(
            name='assertdevicerecord',
            options={'permissions': (('view_assert_device_record', 'can view assert device record'),), 'verbose_name': '设备变更记录', 'verbose_name_plural': '设备变更记录'},
        ),
        migrations.AlterModelOptions(
            name='contractdevice',
            options={'permissions': (('view_contract_device', 'can view contract device'),), 'verbose_name': '采购合同产品明细', 'verbose_name_plural': '采购合同产品明细'},
        ),
        migrations.AlterModelOptions(
            name='faultsolution',
            options={'permissions': (('view_fault_solution', 'can view fault solution'), ('import_fault_solution', 'can import fault_solution'), ('export_fault_solution', 'can export fault_solution'), ('audit_fault_solution', 'can audit fault solution')), 'verbose_name': '故障/问题解决方案', 'verbose_name_plural': '故障/问题解决方案'},
        ),
        migrations.AlterModelOptions(
            name='faulttype',
            options={'permissions': (('view_fault_type', 'can view fault type'),), 'verbose_name': '故障类型', 'verbose_name_plural': '故障类型'},
        ),
        migrations.AlterModelOptions(
            name='maintenanceplan',
            options={'permissions': (('view_maintenance_plan', 'can view maintenance plan'),), 'verbose_name': '设备维护保养计划', 'verbose_name_plural': '设备维护保养计划'},
        ),
        migrations.AlterModelOptions(
            name='medicaldevicesix8cate',
            options={'permissions': (('view_medical_device_six8_cate', 'can view medical device six8 cate'),), 'verbose_name': ' 医疗器械分类(68码)', 'verbose_name_plural': ' 医疗器械分类(68码)'},
        ),
        migrations.AlterModelOptions(
            name='ordereddevice',
            options={'permissions': (('view_ordered_device', 'can view ordered device'),), 'verbose_name': '申购的硬件设备', 'verbose_name_plural': '申购的硬件设备'},
        ),
        migrations.AlterModelOptions(
            name='repairorder',
            options={'permissions': (('view_repair_order', 'can view repair order'), ('dispatch_repair_order', 'can dispatch repair order')), 'verbose_name': '报修单/维修工单', 'verbose_name_plural': '报修单/维修工单'},
        ),
        migrations.AlterModelOptions(
            name='repairorderrecord',
            options={'permissions': (('view_repair_order_record', 'can view repair order record'),), 'verbose_name': '报修单操作记录', 'verbose_name_plural': '报修单操作记录'},
        ),
        migrations.AlterModelOptions(
            name='softwaredevice',
            options={'permissions': (('view_software_device', 'can view software device'),), 'verbose_name': '申购的软件设备', 'verbose_name_plural': '申购的软件设备'},
        ),
    ]