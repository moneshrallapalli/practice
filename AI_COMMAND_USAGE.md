# 🤖 AI Command Center - Usage Guide

## Overview

The AI Command Center allows you to interact with the SentinTinel surveillance system using natural language. Powered by Google Gemini Live API, it understands your commands and executes surveillance tasks in real-time without delay.

## How It Works

### The Flow

```
User Input → Gemini Live API → Context Understanding → Task Execution → Real-time Response
     ↓                                                           ↓
  Natural                                                Scene Analysis
  Language                                               with Active Tasks
```

1. **User sends command** (e.g., "Watch for people entering")
2. **Gemini processes intent** and understands what you want
3. **System confirms** with explanation of what it will do
4. **Background surveillance** continuously analyzes scenes
5. **Task-specific analysis** checks for your requested conditions
6. **Real-time alerts** when conditions are met

## Using the AI Command Center

### Location in Dashboard

The AI Command Center appears in the right sidebar of the dashboard as "🤖 AI Command Center".

### Sending Commands

**Method 1: Type your command**
```
Input field: "Watch for any suspicious activity"
Click: Send button
```

**Method 2: Use Quick Commands**
Click one of the pre-defined quick action buttons:
- 👀 Watch for people
- 🚗 Detect vehicles
- ⚠️ Monitor suspicious activity

### Command Examples

#### Object Detection
```
"Watch for any people entering the building"
"Detect if there are any vehicles in the parking lot"
"Alert me if you see any animals"
"Look for packages or bags left unattended"
```

#### Surveillance Monitoring
```
"Monitor for suspicious activity"
"Watch camera 1 for any movement"
"Track anyone approaching the door"
"Keep an eye on all cameras for unusual behavior"
```

#### Scene Analysis
```
"Describe what's happening in camera 2"
"Analyze the current scene"
"What's going on right now?"
"Give me a summary of all active cameras"
```

#### Anomaly Detection
```
"Alert me if anything unusual happens"
"Monitor for abnormal patterns"
"Detect any anomalies in camera 3"
"Watch for unexpected activity"
```

#### Tracking
```
"Track any person who enters"
"Follow the vehicle that just passed"
"Monitor the same person across cameras"
"Track object movements"
```

## Understanding Responses

### Response Types

1. **Command Processed** (Blue background)
   - Confirmation message
   - Understanding of your intent
   - Task ID for tracking
   - Task type assigned

2. **Task Started** (Blue background)
   - Number of cameras monitoring
   - What the system is looking for
   - Active task confirmation

3. **Task Alert** (Yellow background)
   - Condition detected
   - Details of findings
   - Camera and timestamp

4. **Error** (Red background)
   - Error message
   - Suggested action

### Example Response Flow

**Command:** "Watch for people entering"

**Response 1 - Confirmation:**
```
✓ I will monitor all cameras for people entering
  the building and alert you when detected.

Understanding: Continuous monitoring for people
entering the building

Task: object_detection
```

**Response 2 - Task Started:**
```
Started monitoring on 2 camera(s)
```

**Response 3 - Alert (when person detected):**
```
Person detected entering the scene on camera 1.
Multiple people identified in the frame with
high confidence.
```

## Command Parameters

The AI automatically determines:

- **Which cameras** to monitor (specific or all)
- **What to look for** (objects, activities, patterns)
- **Alert threshold** (low, medium, high priority)
- **Duration** (continuous monitoring or time-limited)
- **Specific conditions** (details to check)

### Specifying Cameras

```
"Watch camera 1 for people"          → Camera 1 only
"Monitor all cameras for vehicles"   → All active cameras
"Check cameras 1 and 2"              → Cameras 1 and 2
```

## Real-Time Context Understanding

The system uses **Gemini Live API** to:

1. **Understand Scene Context**
   - What objects are present
   - What activities are happening
   - Environmental conditions
   - Temporal patterns

2. **Match User Intent**
   - Compare scene against your command
   - Identify relevant detections
   - Calculate confidence scores
   - Generate contextual alerts

3. **Continuous Learning**
   - Build historical context
   - Identify normal patterns
   - Detect deviations
   - Improve accuracy over time

## Task Management

### Active Tasks

All commands create **active tasks** that run continuously until:
- User stops them
- System restart
- Specific duration expires

### Viewing Task Status

Active tasks show in the **AI Responses** section with:
- Task ID
- Task type
- Current status
- Latest findings

### Task Types

The system automatically categorizes your command:

1. **object_detection** - Looking for specific objects
2. **surveillance** - General monitoring
3. **scene_analysis** - Understanding scenes
4. **anomaly_detection** - Finding unusual patterns
5. **tracking** - Following objects/people
6. **alert** - Immediate notifications

## Advanced Features

### Context-Aware Analysis

Every frame is analyzed with:
- **Current scene** - What Gemini sees now
- **Your command** - What you asked for
- **Historical data** - Past similar events
- **Temporal context** - Recent activity

### Intelligent Alerts

Alerts are generated only when:
- Confidence is high
- Matches your specific request
- Significance threshold is met
- Context supports the detection

### Multi-Camera Coordination

The system can:
- Monitor multiple cameras simultaneously
- Correlate events across cameras
- Track objects moving between views
- Provide comprehensive coverage

## Performance Tips

### For Best Results

1. **Be Specific**
   ```
   Good: "Watch for people wearing red jackets"
   Better: "Alert me if someone in red enters camera 1"
   ```

2. **Define Clear Conditions**
   ```
   Good: "Monitor for vehicles"
   Better: "Alert if any vehicle parks in the no-parking zone"
   ```

3. **Specify Cameras When Needed**
   ```
   Good: "Watch for suspicious activity"
   Better: "Monitor camera 2 entrance for suspicious loitering"
   ```

### System Requirements

- **Active Camera**: At least one camera must be running
- **Gemini API**: Valid API key with sufficient quota
- **Network**: Stable connection for real-time processing
- **Processing**: Tasks run at 2 FPS (configurable)

## Limitations

1. **Processing Speed**: Analysis runs at camera FPS (default 2 FPS)
2. **Concurrent Tasks**: Multiple tasks run simultaneously
3. **API Quotas**: Subject to Gemini API rate limits
4. **Accuracy**: Dependent on scene quality and lighting

## Examples by Use Case

### Security Monitoring
```
"Alert me immediately if someone approaches the back door"
"Watch for anyone trying to access restricted areas"
"Monitor for loitering around the entrance"
```

### Traffic Monitoring
```
"Count vehicles entering the parking lot"
"Alert if any vehicle blocks the driveway"
"Watch for delivery trucks"
```

### Safety Monitoring
```
"Detect if anyone falls or needs help"
"Watch for fire or smoke"
"Alert if there's any dangerous activity"
```

### Business Intelligence
```
"Count how many people enter the store"
"Track customer movement patterns"
"Monitor queue lengths"
```

## Troubleshooting

### Command Not Processing

**Check:**
- Camera is active and streaming
- WebSocket connection is established
- Gemini API key is valid
- No error messages in console

**Solution:**
- Refresh the page
- Check browser console for errors
- Verify backend is running

### No Alerts Generated

**Check:**
- Task is confirmed as started
- Camera view includes target area
- Lighting is adequate
- Objects are visible

**Solution:**
- Rephrase command to be more specific
- Lower alert threshold in config
- Check camera angle and positioning

### Delayed Responses

**Check:**
- Network connectivity
- API rate limits
- System resources

**Solution:**
- Reduce FPS in config
- Limit number of active cameras
- Increase processing intervals

## Best Practices

1. **Start Simple**: Test with basic commands first
2. **Monitor Results**: Check AI responses for understanding
3. **Refine Commands**: Adjust based on system feedback
4. **Use Quick Commands**: For common surveillance tasks
5. **Check History**: Review command history for patterns

## Integration with Alerts

Commands automatically integrate with the alert system:

- **Task-specific alerts** appear in Alert Panel
- **Severity** based on task priority
- **Context** includes task details
- **Acknowledgment** marks task alerts as read

## Future Enhancements

Planned features:
- Stop/pause specific tasks
- Task scheduling (time-based)
- Multi-step task chains
- Custom alert rules
- Voice command input
- Mobile app integration

---

**Need Help?**
- Check system logs for details
- Review recent alerts
- Test with quick commands first
- Contact support if issues persist
