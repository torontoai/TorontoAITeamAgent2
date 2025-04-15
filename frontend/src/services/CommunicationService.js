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

/**
 * Communication Service for interacting with the enhanced communication monitoring API
 */
class CommunicationServiceClass {
  /**
   * Base URL for API endpoints
   */
  baseUrl = '/api/communication';

  /**
   * Subscribe to conversation events
   * 
   * @param {Object} filters - Optional filters for the subscription
   * @returns {Promise<Object>} Subscription result with subscriber ID
   */
  async subscribe(filters = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/subscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(filters),
      });

      if (!response.ok) {
        throw new Error(`Failed to subscribe: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error subscribing to conversations:', error);
      throw error;
    }
  }

  /**
   * Unsubscribe from conversation events
   * 
   * @param {string} subscriberId - Subscriber ID to unsubscribe
   * @returns {Promise<Object>} Unsubscription result
   */
  async unsubscribe(subscriberId) {
    try {
      const response = await fetch(`${this.baseUrl}/unsubscribe/${subscriberId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Failed to unsubscribe: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error unsubscribing from conversations:', error);
      throw error;
    }
  }

  /**
   * Get conversation events for a subscriber
   * 
   * @param {string} subscriberId - Subscriber ID
   * @param {number} timeout - Timeout in seconds
   * @returns {Promise<Object>} List of conversation events
   */
  async getConversationEvents(subscriberId, timeout = 0.1) {
    try {
      const response = await fetch(`${this.baseUrl}/events/${subscriberId}?timeout=${timeout}`);

      if (!response.ok) {
        throw new Error(`Failed to get events: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting conversation events:', error);
      throw error;
    }
  }

  /**
   * Get conversation history based on filters
   * 
   * @param {Object} params - Query parameters including filters, limit, and offset
   * @returns {Promise<Object>} Conversation history
   */
  async getConversationHistory(params = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/history`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`Failed to get history: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting conversation history:', error);
      throw error;
    }
  }

  /**
   * Get statistics about conversations
   * 
   * @param {Object} params - Query parameters including time_range and grouping
   * @returns {Promise<Object>} Conversation statistics
   */
  async getConversationStatistics(params = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/statistics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`Failed to get statistics: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting conversation statistics:', error);
      throw error;
    }
  }
}

// Create singleton instance
export const CommunicationService = new CommunicationServiceClass();
