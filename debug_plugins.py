#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pkg_resources
import spreads.plugin as plugin
import spreads.config as config

print("Available plugins via plugin.available_plugins():")
print(plugin.available_plugins())

print("\nEntry points in spreadsplug.hooks:")
for entry_point in pkg_resources.iter_entry_points(group='spreadsplug.hooks'):
    print(f"  {entry_point.name} = {entry_point.module_name}:{entry_point.attrs[0]}")

# Check if WebCommands is properly registered
print("\nLoading 'web' plugin explicitly:")
try:
    web_plugin = next(pkg_resources.iter_entry_points('spreadsplug.hooks', name='web'))
    print(f"  Found entry point: {web_plugin}")
    web_class = web_plugin.load()
    print(f"  Successfully loaded: {web_class.__name__}")
    print(f"  Is subclass of SubcommandHooksMixin: {issubclass(web_class, plugin.SubcommandHooksMixin)}")
except StopIteration:
    print("  Could not find 'web' plugin entry point")
except Exception as e:
    print(f"  Error loading plugin: {e}")

# Check configuration
conf = config.Configuration()
print("\nConfiguration:")
print(f"  Plugins in config: {conf['plugins'].get()}")
print(f"  Raw config data: {conf._config.items()}")
