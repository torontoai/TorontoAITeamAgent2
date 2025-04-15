# TORONTO AI TEAM AGENT - PROPRIETARY
#
# Copyright (c) 2025 TORONTO AI
# Creator: David Tadeusz Chudak
# All Rights Reserved
#
# This file is part of the TORONTO AI TEAM AGENT software.
#
# This software is based on OpenManus (Copyright (c) 2025 manna_and_poem),
# which is licensed under the MIT License. The original license is included
# in the LICENSE file in the root directory of this project.
#
# This software has been substantially modified with proprietary enhancements.


from setuptools import setup, find_packages

setup(
    name="toronto-ai-team-agent-team-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "asyncio",
        "aiohttp",
        "pydantic",
        "pytest",
        "pytest-asyncio",
    ],
    python_requires=">=3.8",
)
