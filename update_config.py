#!/usr/bin/env python
# -*- coding: utf-8 -*-
from spreads.config import Configuration

config = Configuration()
print("Current configuration settings:")
print("Active plugins:", config['plugins'].get())

# Add 'web' to the plugins configuration
config['plugins'] = ['web']

# Save the configuration
config.dump()

print("Updated configuration settings:")
print("Active plugins:", config['plugins'].get())
