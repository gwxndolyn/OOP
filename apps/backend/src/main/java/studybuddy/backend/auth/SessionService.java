package studybuddy.backend.auth;

import jakarta.servlet.http.HttpSession;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import studybuddy.backend.admin.model.UserAccount;
import studybuddy.backend.common.DomainException;
import studybuddy.backend.persistence.StudyRepository;

import java.time.Instant;

@Service
public class SessionService {
    private final StudyRepository repository;

    public SessionService(StudyRepository repository) {
        this.repository = repository;
    }

    public UserAccount account(HttpSession session) {
        Object id = session.getAttribute("accountId");
        UserAccount account =
                repository
                        .find(UserAccount.class, id == null ? "" : id.toString())
                        .orElseThrow(
                                () ->
                                        new DomainException(
                                                HttpStatus.UNAUTHORIZED,
                                                "Choose a demo account to continue."));
        if (!"ACTIVE".equals(account.getStatus()))
            throw DomainException.forbidden("This account is suspended.");
        return account;
    }

    public Actor actor(HttpSession session) {
        return Actor.from(account(session));
    }

    @Transactional
    public UserAccount select(String id, HttpSession session) {
        repository.lock();
        UserAccount account =
                repository
                        .find(UserAccount.class, id)
                        .orElseThrow(() -> DomainException.missing("Account not found."));
        if (!"ACTIVE".equals(account.getStatus()))
            throw DomainException.forbidden("This account is suspended.");
        account.setLastActiveAt(Instant.now());
        repository.save(id, account);
        session.setAttribute("accountId", id);
        return account;
    }
}
