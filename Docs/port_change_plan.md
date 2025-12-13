# Port Change Plan: 8765 → 3000/3001

## Task Overview
Replace all instances of WebSocket port 8765 with ports 3000 and 3001 across the codebase.

## Files to Process (48 files, 50 instances)

### Priority Files (Core Configuration)
- [ ] config.py (1 instance)
- [ ] droxai_config.py (2 instances) 
- [ ] chimera_autarch.py (1 instance)
- [ ] build_release.ps1 (1 instance)

### WebSocket Server Files
- [ ] release\DroxAI\bin\DroxAI_Consumer.py (2 instances)
- [ ] release\DroxAI\bin\DroxAI_Core.py (3 instances)

### Web/Dashboard Files  
- [ ] dashboard.html (2 instances)
- [ ] release\DroxAI\DroxAI_Launcher.py (1 instance)

### Documentation Files
- [ ] DOCKER_GUIDE.md (2 instances)
- [ ] DROXAI_TOWER_INTEGRATION.md (2 instances)
- [ ] DROXAI_USER_GUIDE.md (1 instance)
- [ ] INDEPENDENCE_GUIDE.md (5 instances)
- [ ] README_NEXUS_BUILD.md (2 instances)
- [ ] README_NEXUS.md (2 instances)
- [ ] README.md (2 instances)
- [ ] WINDOWS_GUIDE.md (2 instances)
- [ ] WINDOWS_SERVICE.md (1 instance)
- [ ] YOU_ARE_FREE.md (3 instances)

### Script Files
- [ ] install-service.ps1 (4 instances)
- [ ] launch.sh (1 instance)
- [ ] start_nexus_v3.ps1 (1 instance)
- [ ] start.sh (1 instance)

### Demo/Test Files
- [ ] event_stream_demo.py (2 instances)
- [ ] tests\test_config.py (2 instances)

### Integration Files
- [ ] INTEGRATION_COMPLETE.md (1 instance)
- [ ] PROJECT_STATUS.md (1 instance)

## Port Assignment Strategy
- **3000**: Primary WebSocket port (most instances)
- **3001**: Alternative/configurable WebSocket port (test cases)

## Steps
1. [ ] Backup original files
2. [ ] Create port change script
3. [ ] Replace all 8765 instances with 3000
4. [ ] Replace specific 8765 instances with 3001 where appropriate
5. [ ] Validate changes
6. [ ] Test functionality
7. [ ] Update documentation references

## Estimated Time
45-60 minutes for systematic replacement across all files.
