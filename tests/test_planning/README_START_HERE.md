# START HERE: aws_network_shell Test Strategy

**🎯 Quick Navigation**: Read this first, then dive into detailed docs

---

## 📋 What Happened

Consulted **4 foundational AI models** via RepoPrompt MCP to design a comprehensive test strategy for aws_network_shell CLI with context-dependent commands.

**Models Consulted**:
- ✅ **Kimi K2** (kimi-k2-thinking) - Test Architecture
- ✅ **Nova Premier** (nova-premier) - AWS Expert
- ✅ **Claude Opus 4.5** (claude-opus-4-5-20251101) - Deep Reasoning
- ✅ **DeepSeek V3** (deepseek-v3) - Alternative Perspective

**Result**: Hybrid test strategy combining best of all models

---

## 🎯 The Core Problem

aws_network_shell has **context-dependent commands** where subcommands need parent command outputs:

```bash
aws-network-shell vpc vpc-123        # Sets VPC context
  → show subnets                      # REQUIRES VPC context
    → subnet subnet-456               # Sets subnet context
      → show routes                   # REQUIRES subnet context
```

**Challenge**: How do you test commands that depend on previous command outputs?

**Solution**: Session-based CLIContext with output caching (from Kimi K2)

---

## 📚 Document Guide (Read in Order)

### 1️⃣ Start: EXECUTIVE_SUMMARY.md
**Read Time**: 10 minutes
**Content**: High-level overview, key findings, recommended approach
**Why**: Get the big picture before diving into details

### 2️⃣ Strategy: test_strategy.md (35KB)
**Read Time**: 45 minutes
**Content**: Complete test strategy with code examples, implementation phases
**Why**: Understand the architecture and approach

### 3️⃣ Models: model_consultations.md (20KB)
**Read Time**: 30 minutes
**Content**: Full transcripts of all model consultations (unfiltered)
**Why**: See how different AI models approached the problem

### 4️⃣ Comparison: model_comparison_matrix.md (18KB)
**Read Time**: 20 minutes
**Content**: Side-by-side comparison, strengths/weaknesses, decision matrix
**Why**: Understand why we chose the hybrid approach

### 5️⃣ Implementation: implementation_roadmap.md (19KB)
**Read Time**: 30 minutes
**Content**: Week-by-week breakdown, daily tasks, deliverables
**Why**: Know exactly what to build and when

---

## 🚀 Quick Start (If You Just Want to Start Coding)

### Step 1: Create Directory Structure

```bash
cd /Users/taylaand/code/personal/aws_network_shell

mkdir -p tests/{framework,fixtures,unit,integration,edge_cases}
touch tests/conftest.py
touch tests/framework/{__init__,cli_context,schemas,assertions}.py
touch tests/fixtures/{__init__,network,transit_gateway,cloudwan}.py
```

### Step 2: Install Dependencies

```bash
pip install pytest pytest-cov pytest-xdist moto jsonschema boto3
```

### Step 3: Implement CLIContext Class

Copy this into `tests/framework/cli_context.py`:

```python
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import subprocess
import json

@dataclass
class CLIContext:
    """Session state that accumulates across command executions"""
    env: Dict[str, str] = field(default_factory=dict)
    output_cache: Dict[str, Any] = field(default_factory=dict)
    current_context: List[str] = field(default_factory=list)
    region: str = "us-east-1"

    def execute(self, cmd: str) -> tuple[int, str, str]:
        """Execute command and cache output"""
        full_cmd = ["aws-network-shell"] + self.current_context + cmd.split()
        result = subprocess.run(full_cmd, capture_output=True, text=True)

        cache_key = "_".join(self.current_context + [cmd.split()[0]])
        self.output_cache[cache_key] = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "parsed": self._try_parse_json(result.stdout)
        }

        return result.returncode, result.stdout, result.stderr

    def enter_context(self, context: str):
        self.current_context.append(context)

    def exit_context(self):
        if self.current_context:
            self.current_context.pop()

    def get_cached_output(self, cmd: str) -> Optional[Dict]:
        cache_key = "_".join(self.current_context + [cmd.split()[0]])
        return self.output_cache.get(cache_key)

    def _try_parse_json(self, output: str) -> Optional[Any]:
        try:
            return json.loads(output)
        except:
            return None
```

### Step 4: Write Your First Test

Create `tests/unit/test_vpc_commands.py`:

```python
import pytest
from tests.framework.cli_context import CLIContext

@pytest.fixture
def cli_context():
    return CLIContext()

def test_vpc_list(cli_context):
    """Test vpc list returns valid JSON"""
    exit_code, stdout, stderr = cli_context.execute("vpc list")

    assert exit_code == 0
    assert stdout  # Has output

    # Try to parse as JSON
    import json
    data = json.loads(stdout)
    assert isinstance(data, list)

def test_vpc_context_transition(cli_context):
    """Test entering VPC context and showing subnets"""
    # Get VPC list
    exit_code, stdout, _ = cli_context.execute("vpc list")
    assert exit_code == 0

    # Get first VPC ID from output
    vpc_id = json.loads(stdout)[0]["VpcId"]

    # Enter VPC context
    cli_context.enter_context(f"vpc {vpc_id}")

    # Show subnets in VPC context
    exit_code, stdout, _ = cli_context.execute("show subnets")
    assert exit_code == 0
```

### Step 5: Run Tests

```bash
pytest tests/unit/test_vpc_commands.py -v
```

---

## 🏆 The Recommended Approach

**Hybrid: Kimi K2 + Nova Premier + DeepSeek V3**

### Why This Combination?

| Component | Source | Benefit |
|-----------|--------|---------|
| **Session-based architecture** | Kimi K2 | Solves command dependency problem |
| **Output caching** | Kimi K2 | Enables fixture composition |
| **JSON schema validation** | Kimi K2 | Binary pass/fail |
| **AWS edge cases** | Nova Premier | Real-world scenarios |
| **Multi-region testing** | Nova Premier | Cross-region patterns |
| **Pytest markers** | DeepSeek V3 | Parallelization |
| **Test organization** | DeepSeek V3 | Clear structure |

### Timeline: 4 Weeks

```
Week 1: Foundation (Kimi K2)
├── CLIContext implementation
├── Base fixtures (VPC, subnet, SG)
├── Schema validation
└── 20+ initial tests

Week 2: AWS Integration (Nova Premier)
├── boto3 mocks for all services
├── AWS edge cases (quota limits)
├── Multi-region fixtures
└── 60+ tests total

Week 3: Comprehensive Coverage
├── 100% command coverage
├── Edge case auto-generation
├── Coverage tracking
└── 115+ tests total

Week 4: Optimization (DeepSeek V3)
├── Parallelization (pytest markers)
├── CI/CD integration
├── Performance tuning
└── 145+ tests total
```

---

## 🎓 Key Concepts Explained

### 1. Context Stack

```python
cli_context.current_context = []
# []

cli_context.enter_context("vpc vpc-123")
# ["vpc vpc-123"]

cli_context.enter_context("subnet subnet-456")
# ["vpc vpc-123", "subnet subnet-456"]

# Commands execute as: aws-network-shell vpc vpc-123 subnet subnet-456 <command>
```

### 2. Output Caching

```python
# Execute parent command
exit_code, stdout, _ = cli_context.execute("vpc list")

# Output automatically cached
cached = cli_context.output_cache["vpc_list"]
# {"stdout": "...", "parsed": [...], "exit_code": 0}

# Child fixtures can use cached data
vpcs = cached["parsed"]
vpc_id = vpcs[0]["VpcId"]
```

### 3. Fixture Composition

```python
@pytest.fixture
def vpc_setup(cli_context_factory):
    """Level 1: Create VPC"""
    session = cli_context_factory()
    # ... create VPC ...
    session.enter_context(f"vpc {vpc_id}")
    return session

@pytest.fixture
def subnet_setup(vpc_setup):
    """Level 2: Create subnet using VPC context"""
    session = vpc_setup  # Inherits VPC context!
    # ... create subnet ...
    return session
```

### 4. Schema Validation (Binary Pass/Fail)

```python
VPC_SCHEMA = {
    "type": "array",
    "items": {
        "required": ["VpcId", "CidrBlock"],
        "properties": {
            "VpcId": {"pattern": "^vpc-[a-f0-9]{8,17}$"}
        }
    }
}

# Test: either passes (schema valid) or fails (schema invalid)
# No ambiguity, no subjective interpretation
from jsonschema import validate
validate(instance=data, schema=VPC_SCHEMA)
```

---

## 📊 Success Metrics

### Coverage Targets

| Metric | Target | Approach |
|--------|--------|----------|
| Command Coverage | 100% | Test every CLI command |
| Line Coverage | 80% | Focus on core logic |
| Edge Cases | 90% | AWS limits + invalid inputs |
| Unit Tests | 100+ | Isolated command tests |
| Integration Tests | 20+ | End-to-end workflows |
| Execution Time | <5 min | Parallelization |

### Quality Gates

- ✅ All tests binary pass/fail (no ambiguity)
- ✅ All command paths tested (including context transitions)
- ✅ All fixtures support dependency resolution
- ✅ Schema validation for all JSON outputs
- ✅ 0% flaky tests (deterministic)

---

## 🔧 Common Patterns

### Testing Context Transitions

```python
def test_vpc_to_subnet_workflow(cli_context):
    # Level 1: Get VPC
    exit_code, stdout, _ = cli_context.execute("vpc list")
    vpc_id = json.loads(stdout)[0]["VpcId"]

    # Level 2: Enter VPC context
    cli_context.enter_context(f"vpc {vpc_id}")

    # Level 3: Show subnets in VPC context
    exit_code, stdout, _ = cli_context.execute("show subnets")
    assert exit_code == 0
```

### Testing with Fixtures

```python
def test_subnet_list(vpc_setup):
    """vpc_setup fixture provides VPC context"""
    session = vpc_setup  # Already in VPC context!

    exit_code, stdout, _ = session.execute("show subnets")
    assert exit_code == 0
```

### Schema Validation

```python
from tests.framework.schemas import VPC_LIST_SCHEMA
from jsonschema import validate

def test_vpc_list_schema(cli_context):
    exit_code, stdout, _ = cli_context.execute("vpc list")
    data = json.loads(stdout)

    # Validates or raises ValidationError
    validate(instance=data, schema=VPC_LIST_SCHEMA)
```

---

## 🐛 Troubleshooting

### "Command not found: aws-network-shell"

**Solution**: Update CLIContext to use correct command path
```python
full_cmd = ["python", "-m", "aws_network_shell.cli"] + ...
```

### "Moto mock not working"

**Solution**: Ensure mock decorator is applied
```python
@pytest.fixture
def vpc_setup():
    with mock_ec2():  # Must use context manager
        # ... create VPC ...
```

### "Tests fail intermittently"

**Solution**: Check for shared state between tests
- Ensure fixtures clean up properly
- Use isolated CLIContext per test
- Don't reuse sessions across tests

### "Output parsing fails"

**Solution**: Check output format
- Use `--format json` flag if available
- Handle both JSON and plain text
- Add fallback parsing logic

---

## 🎯 What Makes This Strategy Special

### 1. Multi-Model Validation
- Not just one AI opinion
- 4 different perspectives
- Consensus on fundamentals
- Divergence on implementation details

### 2. Practical Architecture
- Not over-engineered (unlike pure Opus 4.5)
- Not too simple (unlike pure DeepSeek V3)
- Proven patterns (pytest, JSON schemas)
- AWS-aware (Nova Premier expertise)

### 3. Clear Implementation Path
- Week-by-week breakdown
- Daily tasks with hours
- Success criteria at each stage
- Risk mitigation planned

### 4. Production-Ready
- Binary pass/fail (deterministic)
- Schema validation (no format drift)
- Parallelization (fast execution)
- CI/CD integration (automated)

---

## 📞 Next Actions

### Today
1. Read EXECUTIVE_SUMMARY.md (10 minutes)
2. Skim test_strategy.md (20 minutes)
3. Try the Quick Start above (30 minutes)

### This Week
1. Review all documentation (2 hours)
2. Team alignment meeting (1 hour)
3. Set up development environment (1 hour)
4. Start Week 1 implementation (20 hours)

### This Month
- Complete 4-week implementation
- Achieve 90%+ coverage
- Deploy to CI/CD
- Production-ready test framework

---

## 📚 Document Index

| Document | Size | Read Time | Purpose |
|----------|------|-----------|---------|
| **README_START_HERE.md** (this) | - | 10 min | Quick orientation |
| EXECUTIVE_SUMMARY.md | - | 10 min | High-level overview |
| test_strategy.md | 35KB | 45 min | Complete strategy |
| model_consultations.md | 20KB | 30 min | Full AI transcripts |
| model_comparison_matrix.md | 18KB | 20 min | Model comparison |
| implementation_roadmap.md | 19KB | 30 min | Week-by-week plan |

**Total**: ~92KB of comprehensive documentation

---

## 🏁 Bottom Line

**Problem**: CLI with context-dependent commands, no test strategy
**Solution**: Hybrid Kimi K2 + Nova Premier + DeepSeek V3 approach
**Timeline**: 4 weeks (80 hours)
**Outcome**: 145+ tests, 90%+ coverage, <5 min execution

**Start with**: Quick Start section above (30 minutes to first working test)
**Then**: Read EXECUTIVE_SUMMARY.md and test_strategy.md
**Finally**: Follow implementation_roadmap.md week by week

---

**Status**: ✅ Ready for implementation
**Confidence**: High (validated by 4 AI models)
**Risk**: Low (clear roadmap, proven patterns)

**Let's build it!** 🚀
