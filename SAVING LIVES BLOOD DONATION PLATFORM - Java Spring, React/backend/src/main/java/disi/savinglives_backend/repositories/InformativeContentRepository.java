package disi.savinglives_backend.repositories;

import disi.savinglives_backend.entities.InformativeContent;
import disi.savinglives_backend.entities.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public interface InformativeContentRepository  extends JpaRepository<InformativeContent, UUID> {

}
