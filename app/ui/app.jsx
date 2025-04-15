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

import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import EnhancedProjectManagerInterface from './enhanced_project_manager_interface';

// Main App Component
const App = () => {
  return (
    <EnhancedProjectManagerInterface />
  );
};

// Render the app
const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);
