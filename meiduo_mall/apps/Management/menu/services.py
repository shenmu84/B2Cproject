from .models import UmsMenu
class UmsMenuService:
    def update_level(ums_menu):
        if ums_menu.parent_id == 0:
            # 没有父菜单时为一级菜单
            ums_menu.level = 0
        else:
            # 有父菜单时选择根据父菜单level设置
            try:
                # 通过 parent_id 查找父菜单的 UmsMenu 实例
                parent_menu = UmsMenu.objects.get(id=ums_menu.parent_id)
                ums_menu.level = parent_menu.level + 1
            except UmsMenu.DoesNotExist:
                # 如果父菜单不存在，则设置为一级菜单
                ums_menu.level = 0

        ums_menu.save()
