/**
 * TORONTO AI TEAM AGENT - PROPRIETARY
 * 
 * Copyright (c) 2025 TORONTO AI
 * Creator: David Tadeusz Chudak
 * All Rights Reserved
 * 
 * This file is part of the TORONTO AI TEAM AGENT software.
 * 
 * This software is based on OpenManus (Copyright (c) 2025 manna_and_poem),
 * which is licensed under the MIT License. The original license is included
 * in the LICENSE file in the root directory of this project.
 * 
 * This software has been substantially modified with proprietary enhancements.
 */

import React from 'react';
import { Box, Typography, Paper, Grid } from '@mui/material';

function ProjectOverviewPanel() {
  return (
    <>
      <Typography variant="h6" gutterBottom>
        Project Overview
      </Typography>
      <Typography variant="body2" paragraph>
        Status: Completed
      </Typography>
      <Typography variant="body2" paragraph>
        Progress: 100%
      </Typography>
      <Typography variant="body2" paragraph>
        Recent Activity:
      </Typography>
      <Box sx={{ pl: 2 }}>
        <Typography variant="body2" paragraph>
          - Artifacts created: calculator.py and requirements_analysis.md
        </Typography>
      </Box>
    </>
  );
}

export default ProjectOverviewPanel;
