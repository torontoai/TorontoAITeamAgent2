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

import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Heading, 
  Text, 
  Flex, 
  Badge, 
  Select, 
  Input, 
  Button, 
  Divider,
  Spinner,
  useColorModeValue,
  VStack,
  HStack,
  IconButton,
  Tooltip,
  Collapse,
  useDisclosure
} from '@chakra-ui/react';
import { 
  Search, 
  Filter, 
  RefreshCw, 
  Clock, 
  MessageCircle, 
  User, 
  ChevronDown, 
  ChevronUp,
  Download
} from 'react-feather';
import { formatDistanceToNow } from 'date-fns';

import { CommunicationService } from '../services/CommunicationService';

/**
 * Agent Conversation Monitoring Panel
 * 
 * This component provides a real-time view of all conversations happening
 * between agents in the system. It includes filtering, searching, and
 * conversation visualization capabilities.
 */
const AgentConversationMonitoringPanel = ({ projectId }) => {
  // State for conversations
  const [conversations, setConversations] = useState([]);
  const [filteredConversations, setFilteredConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  
  // State for filters
  const [agentFilter, setAgentFilter] = useState('all');
  const [timeRangeFilter, setTimeRangeFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // State for available agents
  const [agents, setAgents] = useState([]);
  
  // State for loading and connection
  const [isLoading, setIsLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('Connecting...');
  
  // WebSocket reference
  const wsRef = useRef(null);
  
  // Subscriber ID for the communication service
  const [subscriberId, setSubscriberId] = useState(null);
  
  // Auto-scroll for messages
  const messagesEndRef = useRef(null);
  
  // Stats panel disclosure
  const { isOpen: isStatsOpen, onToggle: onStatsToggle } = useDisclosure();
  
  // Colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const highlightColor = useColorModeValue('blue.50', 'blue.900');
  
  // Initialize communication service and subscribe to conversations
  useEffect(() => {
    const initCommunication = async () => {
      try {
        setIsLoading(true);
        setConnectionStatus('Connecting to communication service...');
        
        // Subscribe to conversations
        const result = await CommunicationService.subscribe({
          project_id: projectId,
          filters: {}
        });
        
        if (result.success) {
          setSubscriberId(result.subscriber_id);
          setConnectionStatus('Subscription created, establishing WebSocket...');
          
          // Initialize WebSocket connection
          initWebSocket(result.subscriber_id);
        } else {
          setConnectionStatus(`Failed to subscribe: ${result.message}`);
        }
      } catch (error) {
        console.error('Error initializing communication:', error);
        setConnectionStatus(`Connection error: ${error.message}`);
      }
    };
    
    // Load initial conversation history
    const loadConversationHistory = async () => {
      try {
        const result = await CommunicationService.getConversationHistory({
          filters: {},
          limit: 100,
          offset: 0
        });
        
        if (result.success) {
          // Process conversations
          processConversationHistory(result.history);
        }
      } catch (error) {
        console.error('Error loading conversation history:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    // Load available agents
    const loadAgents = async () => {
      try {
        // This would be replaced with an actual API call
        const agentList = [
          { id: 'project_manager', name: 'Project Manager' },
          { id: 'product_manager', name: 'Product Manager' },
          { id: 'developer', name: 'Developer' },
          { id: 'system_architect', name: 'System Architect' },
          { id: 'devops_engineer', name: 'DevOps Engineer' },
          { id: 'qa_testing_specialist', name: 'QA/Testing Specialist' },
          { id: 'security_engineer', name: 'Security Engineer' },
          { id: 'database_engineer', name: 'Database Engineer' },
          { id: 'ui_ux_designer', name: 'UI/UX Designer' },
          { id: 'documentation_specialist', name: 'Documentation Specialist' },
          { id: 'performance_engineer', name: 'Performance Engineer' }
        ];
        
        setAgents(agentList);
      } catch (error) {
        console.error('Error loading agents:', error);
      }
    };
    
    initCommunication();
    loadConversationHistory();
    loadAgents();
    
    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      
      if (subscriberId) {
        CommunicationService.unsubscribe(subscriberId)
          .catch(error => console.error('Error unsubscribing:', error));
      }
    };
  }, [projectId]);
  
  // Initialize WebSocket connection
  const initWebSocket = (subId) => {
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/communication/ws/${subId}`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      setIsConnected(true);
      setConnectionStatus('Connected');
      
      // Send initial ping
      ws.send(JSON.stringify({
        type: 'ping',
        timestamp: new Date().toISOString()
      }));
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'events') {
          // Process conversation events
          processConversationEvents(data.events);
        } else if (data.type === 'pong') {
          // Ping-pong for keeping connection alive
          setTimeout(() => {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({
                type: 'ping',
                timestamp: new Date().toISOString()
              }));
            }
          }, 30000); // Send ping every 30 seconds
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      setConnectionStatus('Disconnected');
      
      // Attempt to reconnect after a delay
      setTimeout(() => {
        if (subscriberId) {
          setConnectionStatus('Reconnecting...');
          initWebSocket(subscriberId);
        }
      }, 5000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus(`Connection error: ${error.message || 'Unknown error'}`);
    };
    
    wsRef.current = ws;
  };
  
  // Process conversation history
  const processConversationHistory = (history) => {
    // Group messages by conversation
    const conversationMap = {};
    
    history.forEach(message => {
      const { conversation_id } = message;
      
      if (!conversationMap[conversation_id]) {
        conversationMap[conversation_id] = {
          id: conversation_id,
          participants: [message.sender, message.recipient],
          messages: [],
          lastMessageTime: null
        };
      }
      
      conversationMap[conversation_id].messages.push(message);
      
      // Update last message time
      const messageTime = new Date(message.timestamp);
      if (!conversationMap[conversation_id].lastMessageTime || 
          messageTime > conversationMap[conversation_id].lastMessageTime) {
        conversationMap[conversation_id].lastMessageTime = messageTime;
      }
    });
    
    // Convert to array and sort by last message time
    const conversationList = Object.values(conversationMap).sort((a, b) => 
      b.lastMessageTime - a.lastMessageTime
    );
    
    setConversations(conversationList);
    applyFilters(conversationList, agentFilter, timeRangeFilter, searchQuery);
  };
  
  // Process real-time conversation events
  const processConversationEvents = (events) => {
    // Process each event
    events.forEach(event => {
      if (event.event_type === 'sent' || event.event_type === 'delivered') {
        const message = event.message;
        const { conversation_id, sender, recipient } = message;
        
        // Update conversations
        setConversations(prevConversations => {
          // Find existing conversation or create new one
          const existingConvIndex = prevConversations.findIndex(c => c.id === conversation_id);
          
          if (existingConvIndex >= 0) {
            // Update existing conversation
            const updatedConversations = [...prevConversations];
            const conversation = { ...updatedConversations[existingConvIndex] };
            
            // Add message if not already present
            if (!conversation.messages.some(m => m.message_id === message.message_id)) {
              conversation.messages = [...conversation.messages, message];
              conversation.lastMessageTime = new Date(message.timestamp);
            }
            
            updatedConversations[existingConvIndex] = conversation;
            
            // If this is the selected conversation, update messages
            if (selectedConversation === conversation_id) {
              setMessages(conversation.messages);
            }
            
            // Sort by last message time
            return updatedConversations.sort((a, b) => 
              b.lastMessageTime - a.lastMessageTime
            );
          } else {
            // Create new conversation
            const newConversation = {
              id: conversation_id,
              participants: [sender, recipient],
              messages: [message],
              lastMessageTime: new Date(message.timestamp)
            };
            
            // Add to list and sort
            return [...prevConversations, newConversation].sort((a, b) => 
              b.lastMessageTime - a.lastMessageTime
            );
          }
        });
      }
    });
  };
  
  // Apply filters to conversations
  const applyFilters = (convList, agent, timeRange, query) => {
    let filtered = [...convList];
    
    // Apply agent filter
    if (agent !== 'all') {
      filtered = filtered.filter(conv => 
        conv.participants.includes(agent)
      );
    }
    
    // Apply time range filter
    if (timeRange !== 'all') {
      const now = new Date();
      let cutoffTime;
      
      switch (timeRange) {
        case 'last_hour':
          cutoffTime = new Date(now.getTime() - 60 * 60 * 1000);
          break;
        case 'last_day':
          cutoffTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
          break;
        case 'last_week':
          cutoffTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          break;
        default:
          cutoffTime = new Date(0); // Beginning of time
      }
      
      filtered = filtered.filter(conv => 
        conv.lastMessageTime >= cutoffTime
      );
    }
    
    // Apply search query
    if (query) {
      const lowerQuery = query.toLowerCase();
      filtered = filtered.filter(conv => {
        // Search in participant names
        if (conv.participants.some(p => p.toLowerCase().includes(lowerQuery))) {
          return true;
        }
        
        // Search in message content
        return conv.messages.some(msg => 
          JSON.stringify(msg.content).toLowerCase().includes(lowerQuery)
        );
      });
    }
    
    setFilteredConversations(filtered);
  };
  
  // Effect to apply filters when they change
  useEffect(() => {
    applyFilters(conversations, agentFilter, timeRangeFilter, searchQuery);
  }, [agentFilter, timeRangeFilter, searchQuery, conversations]);
  
  // Effect to update messages when selected conversation changes
  useEffect(() => {
    if (selectedConversation) {
      const conversation = conversations.find(c => c.id === selectedConversation);
      if (conversation) {
        setMessages(conversation.messages);
      }
    } else {
      setMessages([]);
    }
  }, [selectedConversation, conversations]);
  
  // Auto-scroll to bottom of messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  // Handle conversation selection
  const handleSelectConversation = (conversationId) => {
    setSelectedConversation(conversationId);
  };
  
  // Get agent name from ID
  const getAgentName = (agentId) => {
    const agent = agents.find(a => a.id === agentId);
    return agent ? agent.name : agentId;
  };
  
  // Format message timestamp
  const formatMessageTime = (timestamp) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
    } catch (error) {
      return timestamp;
    }
  };
  
  // Export conversations as JSON
  const exportConversations = () => {
    const dataStr = JSON.stringify(conversations, null, 2);
    const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
    
    const exportFileDefaultName = `conversations_${new Date().toISOString()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };
  
  return (
    <Box 
      borderWidth="1px" 
      borderRadius="lg" 
      overflow="hidden" 
      bg={bgColor}
      height="100%"
      display="flex"
      flexDirection="column"
    >
      <Box p={4} borderBottomWidth="1px" borderColor={borderColor}>
        <Flex justify="space-between" align="center">
          <Heading size="md">Agent Conversations</Heading>
          <HStack>
            <Badge 
              colorScheme={isConnected ? 'green' : 'red'} 
              variant="subtle"
              px={2}
              py={1}
              borderRadius="full"
            >
              {connectionStatus}
            </Badge>
            <Tooltip label="Refresh">
              <IconButton
                icon={<RefreshCw size={16} />}
                size="sm"
                isLoading={isLoading}
                onClick={() => {
                  setIsLoading(true);
                  CommunicationService.getConversationHistory({
                    filters: {},
                    limit: 100,
                    offset: 0
                  })
                    .then(result => {
                      if (result.success) {
                        processConversationHistory(result.history);
                      }
                    })
                    .catch(error => console.error('Error refreshing:', error))
                    .finally(() => setIsLoading(false));
                }}
                aria-label="Refresh conversations"
              />
            </Tooltip>
            <Tooltip label="Export conversations">
              <IconButton
                icon={<Download size={16} />}
                size="sm"
                onClick={exportConversations}
                aria-label="Export conversations"
              />
            </Tooltip>
            <Tooltip label={isStatsOpen ? "Hide statistics" : "Show statistics"}>
              <IconButton
                icon={isStatsOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                size="sm"
                onClick={onStatsToggle}
                aria-label={isStatsOpen ? "Hide statistics" : "Show statistics"}
              />
            </Tooltip>
          </HStack>
        </Flex>
        
        <Collapse in={isStatsOpen} animateOpacity>
          <Box mt={4} p={3} borderWidth="1px" borderRadius="md" borderColor={borderColor}>
            <Heading size="sm" mb={2}>Conversation Statistics</Heading>
            <Flex wrap="wrap" gap={4}>
              <Box>
                <Text fontSize="xs" color="gray.500">Total Conversations</Text>
                <Text fontWeight="bold">{conversations.length}</Text>
              </Box>
              <Box>
                <Text fontSize="xs" color="gray.500">Active Today</Text>
                <Text fontWeight="bold">
                  {conversations.filter(c => {
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    return c.lastMessageTime >= today;
                  }).length}
                </Text>
              </Box>
              <Box>
                <Text fontSize="xs" color="gray.500">Total Messages</Text>
                <Text fontWeight="bold">
                  {conversations.reduce((total, conv) => total + conv.messages.length, 0)}
                </Text>
              </Box>
              <Box>
                <Text fontSize="xs" color="gray.500">Most Active Agent</Text>
                <Text fontWeight="bold">
                  {(() => {
                    const agentCounts = {};
                    conversations.forEach(conv => {
                      conv.messages.forEach(msg => {
                        agentCounts[msg.sender] = (agentCounts[msg.sender] || 0) + 1;
                      });
                    });
                    
                    const mostActiveAgent = Object.entries(agentCounts)
                      .sort((a, b) => b[1] - a[1])[0];
                    
                    return mostActiveAgent ? getAgentName(mostActiveAgent[0]) : 'N/A';
                  })()}
                </Text>
              </Box>
            </Flex>
          </Box>
        </Collapse>
        
        <Flex mt={4} gap={2}>
          <Box flex="1">
            <Input
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leftElement={<Search size={16} />}
            />
          </Box>
          <Select
            value={agentFilter}
            onChange={(e) => setAgentFilter(e.target.value)}
            width="auto"
          >
            <option value="all">All Agents</option>
            {agents.map(agent => (
              <option key={agent.id} value={agent.id}>
                {agent.name}
              </option>
            ))}
          </Select>
          <Select
            value={timeRangeFilter}
            onChange={(e) => setTimeRangeFilter(e.target.value)}
            width="auto"
          >
            <option value="all">All Time</option>
            <option value="last_hour">Last Hour</option>
            <option value="last_day">Last 24 Hours</option>
            <option value="last_week">Last Week</option>
          </Select>
        </Flex>
      </Box>
      
      <Flex flex="1" overflow="hidden">
        {/* Conversation List */}
        <Box 
          width="300px" 
          borderRightWidth="1px" 
          borderColor={borderColor}
          overflowY="auto"
        >
          {isLoading ? (
            <Flex justify="center" align="center" height="100%">
              <Spinner />
            </Flex>
          ) : filteredConversations.length === 0 ? (
            <Flex justify="center" align="center" height="100%" p={4}>
              <Text color="gray.500">No conversations found</Text>
            </Flex>
          ) : (
            <VStack spacing={0} align="stretch">
              {filteredConversations.map(conversation => (
                <Box
                  key={conversation.id}
                  p={3}
                  cursor="pointer"
                  bg={selectedConversation === conversation.id ? highlightColor : 'transparent'}
                  _hover={{ bg: selectedConversation === conversation.id ? highlightColor : useColorModeValue('gray.50', 'gray.700') }}
                  borderBottomWidth="1px"
                  borderColor={borderColor}
                  onClick={() => handleSelectConversation(conversation.id)}
                >
                  <Flex justify="space-between" align="center" mb={1}>
                    <Text fontWeight="bold" fontSize="sm">
                      {conversation.participants.map(p => getAgentName(p)).join(' & ')}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      {formatMessageTime(conversation.lastMessageTime)}
                    </Text>
                  </Flex>
                  <Text fontSize="xs" noOfLines={2} color="gray.600">
                    {conversation.messages.length > 0 
                      ? `${conversation.messages.length} messages`
                      : 'No messages'}
                  </Text>
                </Box>
              ))}
            </VStack>
          )}
        </Box>
        
        {/* Message View */}
        <Box flex="1" display="flex" flexDirection="column" overflow="hidden">
          {selectedConversation ? (
            <>
              <Box p={3} borderBottomWidth="1px" borderColor={borderColor}>
                <Heading size="sm">
                  {(() => {
                    const conversation = conversations.find(c => c.id === selectedConversation);
                    return conversation 
                      ? conversation.participants.map(p => getAgentName(p)).join(' & ')
                      : 'Conversation';
                  })()}
                </Heading>
                <Text fontSize="xs" color="gray.500">
                  {messages.length} messages
                </Text>
              </Box>
              
              <Box flex="1" overflowY="auto" p={3}>
                <VStack spacing={3} align="stretch">
                  {messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp)).map(message => (
                    <Box
                      key={message.message_id}
                      p={3}
                      borderWidth="1px"
                      borderRadius="md"
                      borderColor={borderColor}
                    >
                      <Flex justify="space-between" align="center" mb={2}>
                        <HStack>
                          <Badge colorScheme="blue">
                            {getAgentName(message.sender)}
                          </Badge>
                          <Text fontSize="xs">→</Text>
                          <Badge colorScheme="green">
                            {getAgentName(message.recipient)}
                          </Badge>
                        </HStack>
                        <Tooltip label={new Date(message.timestamp).toLocaleString()}>
                          <Text fontSize="xs" color="gray.500">
                            {formatMessageTime(message.timestamp)}
                          </Text>
                        </Tooltip>
                      </Flex>
                      
                      <Box 
                        p={2} 
                        borderWidth="1px" 
                        borderRadius="md" 
                        borderColor={borderColor}
                        bg={useColorModeValue('gray.50', 'gray.700')}
                        fontSize="sm"
                        fontFamily="monospace"
                      >
                        <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                          {JSON.stringify(message.content, null, 2)}
                        </pre>
                      </Box>
                      
                      {message.delivery_status && (
                        <Flex justify="flex-end" mt={1}>
                          <Badge 
                            size="sm" 
                            colorScheme={message.delivery_status === 'delivered' ? 'green' : 'red'}
                          >
                            {message.delivery_status}
                          </Badge>
                        </Flex>
                      )}
                    </Box>
                  ))}
                  <div ref={messagesEndRef} />
                </VStack>
              </Box>
            </>
          ) : (
            <Flex justify="center" align="center" height="100%">
              <VStack spacing={3}>
                <MessageCircle size={48} color="gray" />
                <Text color="gray.500">Select a conversation to view messages</Text>
              </VStack>
            </Flex>
          )}
        </Box>
      </Flex>
    </Box>
  );
};

export default AgentConversationMonitoringPanel;
