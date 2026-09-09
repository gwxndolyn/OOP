package studybuddy.backend.auth;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import studybuddy.backend.admin.model.UserAccount;
import studybuddy.backend.common.DomainException;
import studybuddy.backend.persistence.StudyRepository;

import java.util.List;
import java.util.Map;

/** Explicit local demonstration login; intentionally has no password authentication. */
@RestController
@RequestMapping("/api/session")
public class SessionController {
    private final SessionService sessions;
    private final StudyRepository repository;
    private final boolean demoEnabled;

    public SessionController(
            SessionService sessions,
            StudyRepository repository,
            @Value("${app.demo.enabled:true}") boolean demoEnabled) {
        this.sessions = sessions;
        this.repository = repository;
        this.demoEnabled = demoEnabled;
    }

    public record AccountChoice(String id, String name, String role) {}

    public record Selection(@NotBlank String accountId) {}

    @GetMapping("/accounts")
    public List<AccountChoice> choices() {
        requireDemo();
        return repository.all(UserAccount.class).stream()
                .filter(a -> "ACTIVE".equals(a.getStatus()))
                .map(a -> new AccountChoice(a.getId(), a.getName(), a.getRole()))
                .toList();
    }

    @PostMapping
    public UserAccount select(@Valid @RequestBody Selection selection, HttpServletRequest request) {
        requireDemo();
        HttpSession session = request.getSession();
        UserAccount account = sessions.select(selection.accountId(), session);
        request.changeSessionId();
        return account;
    }

    @GetMapping
    public UserAccount current(HttpSession session) {
        return sessions.account(session);
    }

    @DeleteMapping
    public Map<String, Boolean> logout(HttpSession session) {
        session.invalidate();
        return Map.of("success", true);
    }

    private void requireDemo() {
        if (!demoEnabled) throw DomainException.forbidden("Demo account selection is disabled.");
    }
}
